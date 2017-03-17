from django.shortcuts import get_object_or_404, render, redirect
from .models import Rental, ItemRental
from django.http import Http404
from django.db import transaction
from django.urls import reverse
import re


@transaction.atomic
def create(request):
    if request.method != 'POST':
        raise Http404
    # get data
    data = request.POST

    params = (
        'name', 'email', 'purpose', 'start_date', 'return_date'
    )

    user = None
    if request.user.is_authenticated:
        user = request.user

    # create Rental object
    rental = Rental(user=user, **{key: data.get(key) for key in params})
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
            item.save()

    return redirect('rental:detail', rental_uuid=rental.uuid)


def detail(request, rental_uuid):
    rental_url = '/rental/' + rental_uuid
    return render(request, 'rental/detail.html', {
        'rental_url': rental_url,
    })


def update(request, rental_id):
    return render(request, 'rental/update.html')
