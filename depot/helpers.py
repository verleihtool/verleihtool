import re
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
