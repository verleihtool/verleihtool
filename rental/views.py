from django.shortcuts import render, redirect

from .models import Rental, ItemRental
from django.db import transaction
from django.views.decorators.http import require_POST
import re

from django.core.mail import send_mail
from django.template import Context
from django.template.loader import render_to_string


@require_POST
@transaction.atomic
def create(request):
    # get data
    data = request.POST

    params = (
        'name', 'depot_id', 'email', 'purpose', 'start_date', 'return_date'
    )

    user = request.user if request.user.is_authenticated else None

    # create Rental object
    rental = Rental(user=user, **{key: data.get(key) for key in params})
    rental.full_clean()
    rental.save()

    # create ItemRental objects
    for key, quantity in data.items():
        m = re.match(r'^item-([0-9]+)-quantity$', key)
        if m is not None and int(quantity) > 0:
            item = ItemRental(
                rental_id=rental.uuid,
                item_id=m.group(1),
                quantity=quantity
            )
            item.full_clean()
            item.save()

    mailcontext = Context({
        'username': rental.name,
        'start_date': rental.start_date,
        'return_date': rental.return_date,
        'id': rental.uuid,
        'itemrental_list': rental.itemrental_set.all()
    })

    html_content = render_to_string('rental_confirmation_email.html', mailcontext)
    txt_content = render_to_string('rental_confirmation_email.txt', mailcontext)

    send_mail(
        'Your rental request, %s ' % rental.name,
        txt_content,
        'su@fs.tum.de',
        [rental.email],
        html_message=html_content,
        fail_silently=True,
    )

    return redirect('rental:detail', rental_uuid=rental.uuid)


def detail(request, rental_uuid):
    rental = get_object_or_404(Rental, pk=rental_uuid)
    dmg = rental.depot.managed_by(request.user)
    item_list = rental.itemrental_set.all()

    return render(request, 'rental/detail.html', {
        'rental': rental,
        'dmg': dmg,
        'item_list': item_list,
    })


def update(request, rental_id):
    return render(request, 'rental/update.html')
