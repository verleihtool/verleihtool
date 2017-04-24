import re
import urllib
import html2text
from django.core.exceptions import ValidationError
from django.core import mail
from django.core.mail import EmailMessage, send_mass_mail
from django.conf import settings
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template import Context
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from depot import availability, helpers
from depot.models import Depot, Item
from .models import Rental, ItemRental
from .state_transitions import allowed_transitions


@require_POST
def create(request):
    """
    Create a new rental object and assign the selected items to it

    When the object is successfully created, the user is redirected
    to the detail view of the new rental.
    If an error occurs, the message dictionary is stored in the
    current session and the user gets back to the edit view to
    correct their mistakes.

    :author: Florian Stamer
    """

    data = request.POST

    user = request.user if request.user.is_authenticated else None

    try:
        # The transaction is cancelled if an unhandled exception occurs
        # in the following block
        with transaction.atomic():
            rental = create_rental(user, data)
            create_items(rental, data)

            send_confirmation_mails(request, rental)

            return redirect('rental:detail', rental_uuid=rental.uuid)
    except ValidationError as e:
        # Store the errors and the submitted data in the current session
        request.session['errors'] = e.message_dict
        request.session['data'] = data

        # Redirect to the form where the errors are displayed
        response = redirect('depot:create_rental', depot_id=data.get('depot_id'))
        response['Location'] += '?' + urllib.parse.urlencode({
            'start_date': data.get('start_date'),
            'return_date': data.get('return_date')
        })

        return response


def detail(request, rental_uuid):
    """
    Provide necessary information for a rentals detail page

    This includes buttons to change the rentals state,
    an alert with information about the rentals state
    and a list of rented items.

    :author: Florian Stamer
    """

    rental = get_object_or_404(Rental, pk=rental_uuid)
    managed_by_user = rental.depot.managed_by(request.user)

    buttons = allowed_transitions(managed_by_user, rental.state)

    alert_classes = {
        Rental.STATE_PENDING: 'info',
        Rental.STATE_REVOKED: 'warning',
        Rental.STATE_APPROVED: 'success',
        Rental.STATE_DECLINED: 'danger',
        Rental.STATE_RETURNED: 'info',
    }

    btn_texts = {
        Rental.STATE_PENDING: 'Pending',
        Rental.STATE_REVOKED: 'Revoke',
        Rental.STATE_APPROVED: 'Approve',
        Rental.STATE_DECLINED: 'Decline',
        Rental.STATE_RETURNED: 'Returned',
    }

    # Copy dictionary so that we can change the copy safely
    btn_classes = alert_classes.copy()
    btn_classes[Rental.STATE_RETURNED] = 'primary'

    return render(request, 'rental/detail.html', {
        'rental': rental,
        'managed_by_user': managed_by_user,
        'buttons': buttons,
        'alert_classes': alert_classes,
        'btn_texts': btn_texts,
        'btn_classes': btn_classes,
    })


@require_POST
def state(request, rental_uuid):
    """
    Change the state of a given rental

    If given an invalid state, this shows a 403 Forbidden response.

    :author: Florian Stamer
    """

    rental = get_object_or_404(Rental, pk=rental_uuid)
    managed_by_user = rental.depot.managed_by(request.user)

    data = request.POST
    state = data.get('state')

    if state not in allowed_transitions(managed_by_user, rental.state):
        return HttpResponseForbidden('Invalid state transition')

    rental.state = state
    rental.save()

    send_state_mails(request, rental)

    return redirect('rental:detail', rental_uuid=rental.uuid)


def create_rental(user, data):
    keys = (
        'firstname', 'lastname', 'depot_id', 'email', 'purpose', 'start_date', 'return_date'
    )
    rental = Rental(user=user, **{key: data.get(key) for key in keys})
    rental.full_clean()
    rental.save()
    # Refresh Rental object to fix issue with depot_id
    rental.refresh_from_db()
    return rental


def create_items(rental, data):
    errors = {}

    item_quantities = helpers.extract_item_quantities(data)

    if not item_quantities:
        raise ValidationError({
            'items': 'The rental cannot be submitted without any items.'
        })

    item_list = Item.objects.filter(id__in=item_quantities.keys())

    item_availability_intervals = availability.get_item_availability_intervals(
        rental.start_date, rental.return_date, rental.depot_id, item_list
    )

    for item, intervals in item_availability_intervals:
        try:
            available = availability.get_minimum_availability(intervals)
            create_item_rental(rental, item, item_quantities[item.id], available)
        except ValidationError as e:
            for key, value in e:
                errors['%s %s' % (item.name, key)] = value

    if errors:
        raise ValidationError(errors)


def create_item_rental(rental, item, quantity, available):
    if quantity > available:
        raise ValidationError({
            'quantity': 'The quantity must not exceed the availability '
                        'of the item in the requested time frame.'
        })

    item_rental = ItemRental(
        rental=rental,
        item=item,
        quantity=quantity
    )
    item_rental.full_clean()
    item_rental.save()


def send_confirmation_mails(request, rental):
    """
    Send emails to requester and dmgs of a depot when a new rental from a depot has been requested
    :author: Stefan Su
    """
    connection = mail.get_connection()
    mailcontext = get_mail_context(request, rental)
    dmg_email_list = get_dmg_emailaddr_list(rental.depot)
    plain_txt_mail_to_requester = html_template_to_txt(
        'rental-confirmation-email.html',
        mailcontext
    )
    plain_txt_mail_to_manager = html_template_to_txt(
        'rental-request-email.html',
        mailcontext
    )
    mail_to_requester = EmailMessage(
        settings.EMAIL_SUBJECT_PREFIX + 'Your rental request, %s %s from depot %s'
        % (rental.firstname, rental.lastname, rental.depot.name),
        plain_txt_mail_to_requester.encode(encoding='utf-8', errors='ignore'),
        settings.DEFAULT_FROM_EMAIL,
        [rental.email],
    )
    mail_to_managers = EmailMessage(
        settings.EMAIL_SUBJECT_PREFIX + 'New rental request by %s %s from depot %s'
        % (rental.firstname, rental.lastname, rental.depot.name),
        plain_txt_mail_to_manager.encode(encoding='utf-8', errors='ignore'),
        settings.DEFAULT_FROM_EMAIL,
        dmg_email_list
    )
    connection.open()
    connection.send_messages([mail_to_requester, mail_to_managers])
    connection.close()


def send_state_mails(request, rental):
    """
    Send an email to the requester when the state of his/her rental has been changed
    :author: Stefan Su
    """
    mailcontext = get_mail_context(request, rental)
    plain_txt_state_change_mail = html_template_to_txt(
        'rental-state-changed-notif-email.html',
        mailcontext
    )
    mail_to_requester = EmailMessage(
        settings.EMAIL_SUBJECT_PREFIX + 'State changed - Your rental request, %s %s from depot %s'
        % (rental.firstname, rental.lastname, rental.depot.name),
        plain_txt_state_change_mail,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[rental.email],
        cc=[settings.DEFAULT_FROM_EMAIL]
    )
    mail_to_requester.send(fail_silently=True)


def get_mail_context(request, rental):
    """
    Get mail context to fill out custom data in mail template
    :param request: is needed for build_absolute_uri() method call
    :param rental:
    :return:
    :author: Stefan Su
    """
    pattern_obj = re.compile("/(create)/")
    mailcontext = Context({
        'firstname': rental.firstname,
        'lastname': rental.lastname,
        'start_date': rental.start_date,
        'return_date': rental.return_date,
        'uuid': rental.uuid,
        'itemrental_list': rental.itemrental_set.all(),
        'absoluteuri': pattern_obj.sub("/", request.build_absolute_uri()),
        'depotname': rental.depot.name,
        'state': rental.get_state_display()
    })
    return mailcontext


def get_dmg_emailaddr_list(depot):
    """
    Get list of email addresses of depot managers within a depot
    :return: list of depot managers
    :author: Stefan Su
    """
    email_list = []

    for dmg in depot.managers:
        email_list += [dmg.email]
    return email_list


def html_template_to_txt(template, context):
    """
    Transforms a html template with context including necessary parameters to a string
    :return: formatted email string
    :author: Stefan Su
    """
    html_content = render_to_string(template, context)
    return html2text.html2text(html_content)
