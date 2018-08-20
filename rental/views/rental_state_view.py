from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from rental.availability import Availability
from rental.state_transitions import allowed_transitions
from rental.models import Rental


class RentalStateView(View):
    """
    Change the state of a given rental

    If given an invalid state, this shows a 403 Forbidden response.

    :author: Florian Stamer
    """

    def check_availability(self, rental):
        availability = Availability(rental.start_date, rental.return_date, rental.depot_id)

        for item_rental in rental.itemrental_set:
            intervals = availability.get_availability_intervals(item_rental.item)
            available = min(intervals).value

            if item_rental.quantity > available:
                raise ValidationError({
                    'quantity': 'The quantity must not exceed the availability '
                                'of the item in the requested time frame.'
                })

    def post(self, request, rental_uuid):
        rental = get_object_or_404(Rental, pk=rental_uuid)
        managed_by_user = rental.depot.managed_by(request.user)

        data = request.POST
        state = data.get('state')
        old_state = data.get('old_state')
        # message = data.get('message')

        if old_state != rental.state:
            return HttpResponseForbidden('The state of the rental request has changed')

        if state not in allowed_transitions(managed_by_user, rental.state):
            return HttpResponseForbidden('Invalid state transition')

        if state == Rental.STATE_APPROVED:
            self.check_availability(rental)

        rental.state = state
        rental.save()

        return redirect('rental:detail', rental_uuid=rental.uuid)
