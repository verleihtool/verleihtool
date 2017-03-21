from django.shortcuts import get_object_or_404, render, redirect
from .models import Rental, ItemRental
from django.http import Http404
from django.db import transaction
from django.urls import reverse
from django.views.decorators.http import require_POST
import re


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
