from datetime import datetime, timedelta
from depot import helpers
from django.shortcuts import render
from django.views import View


class DepotDetailView(View):
    """
    Provide a detailed overview of all items in a depot

    Archived depots can only be accessed by superusers and organization managers.
    The private items of a depot can be seen by all members of this organization.

    :author: Florian Stamer
    """

    def get(self, request, depot_id):
        depot = helpers.get_depot_if_allowed(depot_id, request.user)

        return render(request, 'depot/detail.html', {
            'depot': depot,
            'item_list': helpers.get_item_list(depot, request.user),
            'show_visibility': depot.show_private_items(request.user),
            'managed_by_user': depot.managed_by(request.user),
            'start_date': datetime.now() + timedelta(days=1),
            'return_date': datetime.now() + timedelta(days=4)
        })
