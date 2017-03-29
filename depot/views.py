from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Depot, Item, Organization
from datetime import datetime, timedelta
from .availability import get_availability_intervals, get_maximum_availability
from rental.models import Rental


def index(request):
    """
    Show an index page of all organizations and their depots

    Only organization managers get a link to the admin interface of their
    organization so that they can change the name and add new depots.

    :author: Florian Stamer
    :author: Benedikt Seidl
    """

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
    """
    Provide a detailed overview of all items in a depot

    Archived depots can only be accessed by superusers and organization managers.
    The private items of a depot can be seen by all members of this organization.

    :author: Florian Stamer
    """

    depot = get_object_or_404(Depot, pk=depot_id)

    if not depot.organization.managed_by(request.user) and not depot.active:
        return HttpResponseForbidden()

    # configure time frame
    start = datetime.now() + timedelta(minutes=5)
    end = datetime.now() + timedelta(days=3)
    if request.method == 'POST':
        data = request.POST
        start = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M')
        end = datetime.strptime(data.get('return_date'), '%Y-%m-%d %H:%M')

    show_visibility = (request.user.is_superuser or
                       depot.organization.is_member(request.user))

    if show_visibility:
        item_list = depot.item_set.all()
    else:
        item_list = depot.public_items.all()

    item_availability_list = get_item_availability_list(start, end, depot_id, item_list)

    start = start.strftime('%Y-%m-%d %H:%M')
    end = end.strftime('%Y-%m-%d %H:%M')

    error_message = None
    if 'message' in request.session:
        error_message = request.session['message']
        request.session.__delitem__('message')

    return render(request, 'depot/detail.html', {
        'depot': depot,
        'show_visibility': show_visibility,
        'managed_by_user': depot.managed_by(request.user),
        'item_availability_list': item_availability_list,
        'error_message': error_message,
        'start': start,
        'end': end,
    })


def get_item_availability_list(from_date, to_date, depot_id, item_list):
    """
    Calculate availability for each item in item_list

    :return: A list of availabilities
    """

    rentals = Rental.objects.filter(
        start_date__lt=to_date,
        return_date__gt=from_date,
        depot_id=depot_id,
        state=Rental.STATE_APPROVED
    )
    availability_list = []
    for item in item_list:
        intervals = get_availability_intervals(from_date, to_date, item, rentals)
        availability_list.append(
            (item, get_maximum_availability(intervals))
        )

    return availability_list


def rentals(request, depot_id):
    """
    Provides an overview over all rentals for one depot

    Show labels to visually differentiate the state a
    rental is in.

    :author: Florian Stamer
    """

    depot = get_object_or_404(Depot, pk=depot_id)

    if not depot.managed_by(request.user):
        return HttpResponseForbidden()

    rentals = Rental.objects.filter(depot_id=depot.id)
    state_labels = {
        Rental.STATE_PENDING: 'label label-info',
        Rental.STATE_REVOKED: 'label label-warning',
        Rental.STATE_APPROVED: 'label label-success',
        Rental.STATE_DECLINED: 'label label-danger',
        Rental.STATE_RETURNED: 'label label-default',
    }

    return render(request, 'depot/rentals.html', {
        'rentals': rentals,
        'depot': depot,
        'state_labels': state_labels,
    })
