from django.shortcuts import render, get_object_or_404
from django.views import View
from rental.models import Rental
from rental.state_transitions import allowed_transitions


class RentalDetailView(View):
    """
    Provide necessary information for a rentals detail page

    This includes buttons to change the rentals state,
    an alert with information about the rentals state
    and a list of rented items.

    :author: Florian Stamer
    """

    def get(self, request, rental_uuid):
        rental = get_object_or_404(Rental, pk=rental_uuid)
        managed_by_user = rental.depot.managed_by(request.user)

        states = allowed_transitions(managed_by_user, rental.state)

        btn_texts = {
            Rental.STATE_PENDING: 'Reset',
            Rental.STATE_REVOKED: 'Revoke',
            Rental.STATE_APPROVED: 'Approve',
            Rental.STATE_DECLINED: 'Decline',
            Rental.STATE_RETURNED: 'Close',
        }

        return render(request, 'rental/detail.html', {
            'rental': rental,
            'managed_by_user': managed_by_user,
            'states': states,
            'btn_texts': btn_texts,
        })
