import re
from datetime import datetime, timedelta
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from depot.models import Depot


def get_depot_if_allowed(depot_id, user):
    """
    Return the depot for the given if the user is allowed to access it

    Otherwise throws a PermissionDenied exception.

    :author: Benedikt Seidl
    """

    depot = get_object_or_404(Depot, pk=depot_id)

    if not depot.organization.managed_by(user) and not depot.active:
        raise PermissionDenied('Depot is not active')

    return depot


def get_item_list(depot, user):
    """
    Return the list of items the user is allowed to see in this depot

    :author: Benedikt Seidl
    """

    if depot.show_private_items(user):
        return depot.active_items.all()
    else:
        return depot.public_items.all()


def get_start_return_date(data):
    """
    Return the start and return dates from the request

    If required data is missing or invalid, default values are returned.

    :author: Benedikt Seidl
    """

    try:
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M')
    except:
        start_date = datetime.now() + timedelta(days=1)

    try:
        return_date = datetime.strptime(data.get('return_date'), '%Y-%m-%d %H:%M')
    except:
        return_date = start_date + timedelta(days=3)

    return (start_date, max(start_date, return_date))


def extract_item_quantities(data):
    """
    Extract the item quantities from the provided dictionary

    The format matches the input names of the rental creation form.
    Only positive quantities are considered.

    :author: Benedikt Seidl
    """

    item_quantities = {}
    for key, quantity in data.items():
        m = re.match(r'^item-([0-9]+)-quantity$', key)
        if m is not None and int(quantity) > 0:
            item_quantities[int(m.group(1))] = int(quantity)

    return item_quantities


def get_chart_data(intervals):
    """
    Generate the data the JavaScript can render

    :author: Benedikt Seidl
    """

    data = []

    for begin, end, availability in intervals:
        data.append({
            "x": begin.isoformat(),
            "y": availability
        })
        data.append({
            "x": end.isoformat(),
            "y": availability
        })

    return data
