from django.shortcuts import render, redirect, get_object_or_404

from .models import Rental, ItemRental
from depot.models import Depot
from django.db import transaction
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.mail import send_mass_mail
from django.template import Context
from django.template.loader import render_to_string
from django.http import HttpResponseForbidden
import re
import html2text


@require_POST
def create(request):
    data = request.POST

    params = (
        'firstname', 'lastname', 'depot_id', 'email', 'purpose', 'start_date', 'return_date'
    )

    user = request.user if request.user.is_authenticated else None

    try:
        with transaction.atomic():
            rental = create_rental(request.session, user, params, data)

            if create_items(request.session, rental, data):
                create_session_msg(
                    request.session,
                    ValidationError({
                        'items': 'The rental cannot be submitted without any items.'
                    })
                )

            if 'message' in request.session and request.session['message'] is not None:
                raise ValidationError('Errors occured.')

            send_confirmation_mails(request, rental)

            return redirect('rental:detail', rental_uuid=rental.uuid)
    except ValidationError:
        return redirect('depot:detail', depot_id=data.get('depot_id'))


def detail(request, rental_uuid):
    """
    Provides necessary information for a rentals detail page

    This includes buttons to change the rentals state,
    an alert with information about the rentals state
    and a list of rented items.

    :author: Florian Stamer
    """

    rental = get_object_or_404(Rental, pk=rental_uuid)
    depot = get_object_or_404(Depot, pk=rental.depot_id)
    dmg = rental.depot.managed_by(request.user)
    item_list = rental.itemrental_set.all()
    buttons = []
    pending = {'class': 'btn btn-info', 'value': 'Pending'}
    revoke = {'class': 'btn btn-warning', 'value': 'Revoke'}
    approve = {'class': 'btn btn-success', 'value': 'Approve'}
    decline = {'class': 'btn btn-danger', 'value': 'Decline'}
    returned = {'class': 'btn btn-primary', 'value': 'Returned'}

    alert = 'alert alert-info'
    if rental.state == Rental.STATE_PENDING:
        buttons.append(revoke)
        if dmg:
            buttons.append(approve)
            buttons.append(decline)
    elif rental.state == Rental.STATE_APPROVED:
        alert = 'alert alert-success'
        buttons.append(revoke)
        if dmg:
            buttons.append(pending)
            buttons.append(decline)
            buttons.append(returned)
    elif rental.state == Rental.STATE_DECLINED:
        alert = 'alert alert-danger'
        if dmg:
            buttons.append(pending)
            buttons.append(approve)
    elif rental.state == Rental.STATE_RETURNED:
        if dmg:
            buttons.append(approve)
    else:
        alert = 'alert alert-warning'
        buttons.append(pending)

    return render(request, 'rental/detail.html', {
        'rental': rental,
        'depot': depot,
        'buttons': buttons,
        'item_list': item_list,
        'alert': alert,
    })


@require_POST
def state(request, rental_uuid):
    """
    Changes state of a given rental

    If given an invalid state, return 403.

    :author: Florian Stamer
    """

    rental = get_object_or_404(Rental, pk=rental_uuid)
    data = request.POST
    dmg = rental.depot.managed_by(request.user)
    state = data.get('state')
    states = {
        'Pending': Rental.STATE_PENDING,
        'Revoke': Rental.STATE_REVOKED,
        'Approve': Rental.STATE_APPROVED,
        'Decline': Rental.STATE_DECLINED,
        'Returned': Rental.STATE_RETURNED
    }

    if not valid_state_change(dmg, rental.state, state):
        return HttpResponseForbidden()

    rental.state = states[state]
    rental.save()
    return redirect('rental:detail', rental_uuid=rental.uuid)


def update(request, rental_uuid):
    return render(request, 'rental/update.html')


def valid_state_change(dmg, state, action):
    if dmg:
        valid = {
            Rental.STATE_PENDING: ['Revoke', 'Approve', 'Decline'],
            Rental.STATE_REVOKED: ['Pending'],
            Rental.STATE_APPROVED: ['Pending', 'Revoke', 'Decline', 'Returned'],
            Rental.STATE_DECLINED: ['Pending', 'Approve'],
            Rental.STATE_RETURNED: ['Approve']
        }
    else:
        valid = {
            Rental.STATE_PENDING: ['Revoke'],
            Rental.STATE_REVOKED: ['Pending'],
            Rental.STATE_APPROVED: ['Revoke'],
            Rental.STATE_DECLINED: [],
            Rental.STATE_RETURNED: []
        }

    return action in valid[state]


def create_session_msg(session, e):
    if 'message' not in session:
        session['message'] = []
    for key, message in e:
        session['message'].append(key + ': ' + str(message))


def create_rental(session, user, params, data):
    rental = Rental(user=user, **{key: data.get(key) for key in params})
    try:
        rental.full_clean()
        rental.save()
    except ValidationError as e:
        create_session_msg(session, e)
        rental = Rental(
            user=None,
            depot_id=data.get('depot_id'),
            firstname='De',
            lastname='Bug',
            email='debug@example.com',
            start_date='1999-12-31',
            return_date='2000-01-01'
        )
        rental.save()
    return rental


def create_items(session, rental, data):
    empty = True
    for key, quantity in data.items():
        m = re.match(r'^item-([0-9]+)-quantity$', key)
        if m is not None and int(quantity) > 0:
            empty = False
            item = ItemRental(
                rental_id=rental.uuid,
                item_id=m.group(1),
                quantity=quantity
            )
            try:
                item.full_clean()
                item.save()
            except ValidationError as e:
                create_session_msg(session, e)
    return empty


def send_confirmation_mails(request, rental):
    pattern_obj = re.compile("/(create)/")

    mailcontext = Context({
        'firstname': rental.firstname,
        'lastname': rental.lastname,
        'start_date': rental.start_date,
        'return_date': rental.return_date,
        'uuid': rental.uuid,
        'itemrental_list': rental.itemrental_set.all(),
        'absoluteuri': pattern_obj.sub("/", request.build_absolute_uri()),
        'depotname': rental.depot.name
    })

    dmg_email_list = get_dmg_emailaddr_list(rental.depot.managers)

    plain_txt_mail_to_requester = html_template_to_txt(
        'rental-confirmation-email.html',
        mailcontext
    )

    plain_txt_mail_to_manager = html_template_to_txt(
        'rental-request-email.html',
        mailcontext
    )

    mail_to_requester = (
        '[Verleihtool] Your rental request, %s %s from depot %s'
        % (rental.lastname, rental.firstname, rental.depot.name),
        plain_txt_mail_to_requester,
        'verleih@fs.tum.de',
        [rental.email],
    )

    mail_to_managers = (
        '[Verleihtool] New rental request by %s %s from depot %s'
        % (rental.lastname, rental.firstname, rental.depot.name),
        plain_txt_mail_to_manager,
        'verleih@fs.tum.de',
        dmg_email_list
    )

    send_mass_mail((mail_to_requester, mail_to_managers), fail_silently=True)


def get_dmg_emailaddr_list(depot_managers):
    email_list = []
    for dmg in depot_managers:
        email_list += [dmg.email]
    return email_list


def html_template_to_txt(template, context):
    html_content = render_to_string(template, context)
    return html2text.html2text(html_content)
