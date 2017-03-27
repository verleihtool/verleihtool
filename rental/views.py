from django.shortcuts import render, redirect, get_object_or_404

from depot.models import Depot
from .models import Rental, ItemRental
from django.db import transaction
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.mail import send_mass_mail
from django.template import Context
from django.template.loader import render_to_string
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
    rental = get_object_or_404(Rental, pk=rental_uuid)
    dmg = rental.depot.managed_by(request.user)
    item_list = rental.itemrental_set.all()
    if rental.state == Rental.STATE_PENDING:
        alert = "alert alert-info"
    elif rental.state == Rental.STATE_APPROVED:
        alert = "alert alert-success"
    elif rental.state == Rental.STATE_DECLINED:
        alert = "alert alert-danger"
    else:
        alert = "alert alert.warning"

    return render(request, 'rental/detail.html', {
        'rental': rental,
        'dmg': dmg,
        'item_list': item_list,
        'alert': alert,
    })


def update(request, rental_id):
    return render(request, 'rental/update.html')


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

    html_content_mail_to_requester = render_to_string(
        'rental_confirmation_email.html',
        mailcontext
    )

    plain_txt_mail_to_requester = html2text.html2text(html_content_mail_to_requester)

    mail_to_requester = (
        'Your rental request, %s %s' % (rental.lastname, rental.firstname),
        plain_txt_mail_to_requester,
        'verleih@tool.de',
        [rental.email],
    )

    plain_txt_mail_to_manager = ''

    dmg_email_list = get_dmg_emailaddr_list(rental.depot.managers)

    mail_to_managers = (
        'New rental request by %s %s' % (rental.lastname, rental.firstname),
        plain_txt_mail_to_manager,
        'verleih@tool.de',
        dmg_email_list
    )

    send_mass_mail(mail_to_requester, mail_to_managers)


def get_dmg_emailaddr_list(depot_managers):
    email_list = []
    for dmg in depot_managers:
        email_list += dmg.email
    return email_list
