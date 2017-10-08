from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from rental.state_transitions import allowed_transitions
from rental.models import Rental


class RentalStateView(View):
    """
    Change the state of a given rental

    If given an invalid state, this shows a 403 Forbidden response.

    :author: Florian Stamer
    """

    def post(self, request, rental_uuid):
        rental = get_object_or_404(Rental, pk=rental_uuid)
        managed_by_user = rental.depot.managed_by(request.user)

        data = request.POST
        state = data.get('state')

        if state not in allowed_transitions(managed_by_user, rental.state):
            return HttpResponseForbidden('Invalid state transition')

        rental.state = state
        rental.save()

        return redirect('rental:detail', rental_uuid=rental.uuid)
