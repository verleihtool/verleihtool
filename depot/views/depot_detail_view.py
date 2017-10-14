from datetime import datetime, timedelta
from depot.helpers import get_depot_if_allowed
from django.shortcuts import render
from django.views import View
from depot import wikidata


class DepotDetailView(View):
    """
    Provide a detailed overview of all items in a depot

    Archived depots can only be accessed by superusers and organization managers.
    The private items of a depot can be seen by all members of this organization.

    :author: Florian Stamer
    """

    def get(self, request, depot_id):
        depot = get_depot_if_allowed(depot_id, request.user)
        item_list = depot.visible_items(request.user)
        labels = wikidata.get_labels(item_list, lang='de')

        return render(request, 'depot/detail.html', {
            'depot': depot,
            'item_list': item_list,
            'labels': labels,
            'show_visibility': depot.show_private_items(request.user),
            'managed_by_user': depot.managed_by(request.user),
            'start_date': datetime.now() + timedelta(days=1),
            'return_date': datetime.now() + timedelta(days=4)
        })
