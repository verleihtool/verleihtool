from depot.models import Depot
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views import View
from rental.models import Rental


class DepotRentalsView(View):
    """
    Provide an overview over all rentals for one depot

    Show labels to visually differentiate the state a
    rental is in.

    :author: Florian Stamer
    """

    def get(self, request, depot_id):
        depot = get_object_or_404(Depot, pk=depot_id)

        if not depot.managed_by(request.user):
            return HttpResponseForbidden('Not a manager of this depot')

        rentals = Rental.objects.filter(depot_id=depot.id)

        return render(request, 'depot/rentals.html', {
            'rentals': rentals,
            'depot': depot,
        })
