from django.shortcuts import get_object_or_404, render, redirect
from .models import Rental, ItemRental
from django.http import Http404
from django.db import transaction
import re

# Create your views here.

@transaction.atomic
def create(request):
    if request.method != 'POST':
        raise Http404
    #get data
    data = request.POST
    #parse data
    name = data.get(name)
    email = data.get(email)
    purpose = data.get(purpose)
    user = data.get(user)
    start_date = data.get(start_date)
    return_date = data.get(return_date)

    #create Rental object
    rental = Rental(name, email, purpose, user, start_date, return_date)
    rental.save()

    #create ItemRental objects
    for key, quantity in data.dict():
        m = re.match(r'^item-([0-9]+)-quantity$', key)
        if m not None:
            item = ItemRental(
                rental_id=rental.uuid,
                item_id=m.group(0), 
                quantity=quantity
            )
            item.save()
            rental.items.add(item)

    return redirect('detail', rental_id=rental.uuid)


def detail(request, rental_id):
    return render(request, 'rental/detail.html')


def update(request, rental_id):
    return render(request, 'rental/update.html')
