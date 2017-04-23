from datetime import datetime, timedelta
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from depot.models import Depot, Item


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


def show_private_items(depot, user):
    return user.is_superuser or depot.organization.is_member(user)


def get_item_list(depot, user):
    """
    Return the list of items the user is allowed to see in this depot

    :author: Benedikt Seidl
    """

    if show_private_items(depot, user):
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
