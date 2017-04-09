import re
import urllib
import html2text
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template import Context
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from depot import availability, helpers
from depot.models import Depot, Item
from .models import Rental, ItemRental


@require_POST
def create(request):
    data = request.POST

    user = request.user if request.user.is_authenticated else None

    try:
        with transaction.atomic():
            rental = create_rental(user, data)
            create_items(rental, data)

            send_confirmation_mail(request, rental)

            return redirect('rental:detail', rental_uuid=rental.uuid)
    except ValidationError as e:
        request.session['errors'] = e.message_dict
        request.session['data'] = data
        response = redirect('depot:create_rental', depot_id=data.get('depot_id'))
        response['Location'] += '?' + urllib.parse.urlencode({
            'start_date': data.get('start_date'),
            'return_date': data.get('return_date')
        })
        return response


# Allowed state transitions for managers of the connected depot
STATE_TRANSITIONS_MANAGER = {
    Rental.STATE_PENDING: [
        Rental.STATE_REVOKED,
        Rental.STATE_APPROVED,
        Rental.STATE_DECLINED,
    ],
    Rental.STATE_REVOKED: [
        Rental.STATE_PENDING,
    ],
    Rental.STATE_APPROVED: [
        Rental.STATE_PENDING,
        Rental.STATE_REVOKED,
        Rental.STATE_DECLINED,
        Rental.STATE_RETURNED,
    ],
    Rental.STATE_DECLINED: [
        Rental.STATE_PENDING,
        Rental.STATE_APPROVED,
    ],
    Rental.STATE_RETURNED: [
        Rental.STATE_APPROVED,
    ]
}

# Allowed state transitions for any other user
STATE_TRANSITIONS_USER = {
    Rental.STATE_PENDING: [
        Rental.STATE_REVOKED,
    ],
    Rental.STATE_REVOKED: [
        Rental.STATE_PENDING,
    ],
    Rental.STATE_APPROVED: [
        Rental.STATE_REVOKED,
    ],
    Rental.STATE_DECLINED: [],
    Rental.STATE_RETURNED: [],
}


def detail(request, rental_uuid):
    """
    Provides necessary information for a rentals detail page

    This includes buttons to change the rentals state,
    an alert with information about the rentals state
    and a list of rented items.

    :author: Florian Stamer
    """

    rental = get_object_or_404(Rental, pk=rental_uuid)
    managed_by_user = rental.depot.managed_by(request.user)

    if managed_by_user:
        buttons = STATE_TRANSITIONS_MANAGER[rental.state]
    else:
        buttons = STATE_TRANSITIONS_USER[rental.state]

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
    Changes state of a given rental

    If given an invalid state, return 403.

    :author: Florian Stamer
    """

    rental = get_object_or_404(Rental, pk=rental_uuid)
    managed_by_user = rental.depot.managed_by(request.user)

    data = request.POST
    state = data.get('state')

    if not valid_state_transition(managed_by_user, rental.state, state):
        return HttpResponseForbidden('Invalid state transition')

    rental.state = state
    rental.save()

    return redirect('rental:detail', rental_uuid=rental.uuid)


def valid_state_transition(managed_by_user, old_state, new_state):
    if managed_by_user:
        return new_state in STATE_TRANSITIONS_MANAGER[old_state]
    else:
        return new_state in STATE_TRANSITIONS_USER[old_state]


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

    for item, avail in get_item_availabilities(rental, item_quantities):
        try:
            create_item_rental(rental, item, item_quantities[item.id], avail)
        except ValidationError as e:
            for key, value in e:
                errors['%s %s' % (item.name, key)] = value

    if errors:
        raise ValidationError(errors)


def get_item_availabilities(rental, item_quantities):
    item_list = Item.objects.filter(id__in=item_quantities.keys())

    return availability.get_item_availability_list(
        rental.start_date,
        rental.return_date,
        rental.depot_id,
        item_list
    )


def create_item_rental(rental, item, quantity, availability):
    if quantity > availability:
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


def send_confirmation_mail(request, rental):
    pattern_obj = re.compile("/(create)/")

    mailcontext = {
        'firstname': rental.firstname,
        'lastname': rental.lastname,
        'start_date': rental.start_date,
        'return_date': rental.return_date,
        'uuid': rental.uuid,
        'itemrental_list': rental.itemrental_set.all(),
        'absoluteuri': pattern_obj.sub("/", request.build_absolute_uri())
    }

    html_content = render_to_string('rental_confirmation_email.html', mailcontext)
    plain_txt_mail = html2text.html2text(html_content)

    send_mail(
        'Your rental request, %s %s' % (rental.lastname, rental.firstname),
        plain_txt_mail,
        'verleih@tool.de',
        [rental.email],
        html_message=html_content,
        fail_silently=True,
    )
