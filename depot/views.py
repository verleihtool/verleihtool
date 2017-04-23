from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from depot.models import Depot, Organization
from rental.models import Rental
from datetime import datetime, timedelta
from . import availability, helpers


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

    depot = helpers.get_depot_if_allowed(depot_id, request.user)

    return render(request, 'depot/detail.html', {
        'depot': depot,
        'item_list': helpers.get_item_list(depot, request.user),
        'show_visibility': helpers.show_private_items(depot, request.user),
        'managed_by_user': depot.managed_by(request.user),
        'start_date': datetime.now() + timedelta(days=1),
        'return_date': datetime.now() + timedelta(days=4)
    })


def rentals(request, depot_id):
    """
    Provide an overview over all rentals for one depot

    Show labels to visually differentiate the state a
    rental is in.

    :author: Florian Stamer
    """

    depot = get_object_or_404(Depot, pk=depot_id)

    if not depot.managed_by(request.user):
        return HttpResponseForbidden('Not a manager of this depot')

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


def create_rental(request, depot_id):
    """
    Show a form to create a new rental for the given depot

    :author: Benedikt Seidl
    """

    depot = helpers.get_depot_if_allowed(depot_id, request.user)

    # configure time frame
    start_date, return_date = helpers.get_start_return_date(request.GET)

    item_list = helpers.get_item_list(depot, request.user)
    item_availability_intervals = availability.get_item_availability_intervals(
        start_date, return_date, depot_id, item_list
    )

    availability_data = []
    for item, intervals in item_availability_intervals:
        availability_data.append((
            item,
            helpers.get_chart_data(intervals),
            availability.get_minimum_availability(intervals)
        ))

    errors = request.session.pop('errors', None)
    data = request.session.pop('data', {})

    return render(request, 'depot/create-rental.html', {
        'depot': depot,
        'show_visibility': helpers.show_private_items(depot, request.user),
        'availability_data': availability_data,
        'errors': errors,
        'data': data,
        'item_quantities': helpers.extract_item_quantities(data),
        'start_date': start_date,
        'return_date': return_date,
        'start_date_formatted': start_date.strftime('%Y-%m-%d %H:%M'),
        'return_date_formatted': return_date.strftime('%Y-%m-%d %H:%M')
    })
