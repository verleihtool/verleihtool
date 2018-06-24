from datetime import datetime, timedelta
from depot.helpers import get_depot_if_allowed
from django.shortcuts import render
from django.views import View


class DepotDetailView(View):
    """
    Provide a detailed overview of all items in a depot

    Archived depots can only be accessed by superusers and organization managers.
    The internal items of a depot can be seen by all members of this organization.

    :author: Florian Stamer
    """

    def get(self, request, depot_id):
        depot = get_depot_if_allowed(depot_id, request.user)
        item_list = depot.visible_items(request.user)

        return render(request, 'depot/detail.html', {
            'depot': depot,
            'item_list': item_list,
            'show_visibility': depot.show_internal_items(request.user),
            'managed_by_user': depot.managed_by(request.user),
            'start_date': datetime.now() + timedelta(days=1),
            'return_date': datetime.now() + timedelta(days=4)
        })
