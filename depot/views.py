from django.shortcuts import render, get_object_or_404
from .models import Depot, Item, Organization


def index(request):
    return render(request, 'depot/index.html', {
        'organizations': Organization.objects.all()
    })


def detail(request, depot_id):
    if request.user.is_superuser:
        depot = get_object_or_404(Depot, pk=depot_id)
    else:
        depot = get_object_or_404(Depot, pk=depot_id, active=True)

    if request.user.is_authenticated:
        item_list = depot.item_set.all()
    else:
        item_list = depot.public_items.all()

    return render(request, 'depot/detail.html', {
        'depot': depot,
        'managed_by_user': depot.managed_by(request.user),
        'item_list': item_list,
    })
