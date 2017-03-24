from django.shortcuts import render, get_object_or_404
from .models import Depot, Item, Organization


def index(request):
    organization_depots = []

    for organization in Organization.objects.all():
        managed_by_user = organization.managed_by(request.user)
        if managed_by_user:
            depots = organization.depot_set.all()
        else:
            depots = organization.active_depots.all()

        if depots:
            organization_depots.append({
                'model': organization,
                'managed_by_user': managed_by_user,
                'depots': depots
            })


    return render(request, 'depot/index.html', {
        'organization_depots': organization_depots
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
