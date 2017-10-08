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

        alert_classes = {
            Rental.STATE_PENDING: 'info',
            Rental.STATE_REVOKED: 'warning',
            Rental.STATE_APPROVED: 'success',
            Rental.STATE_DECLINED: 'danger',
            Rental.STATE_RETURNED: 'info',
        }

        btn_texts = {
            Rental.STATE_PENDING: 'Pending',
            Rental.STATE_REVOKED: 'Revoke',
            Rental.STATE_APPROVED: 'Approve',
            Rental.STATE_DECLINED: 'Decline',
            Rental.STATE_RETURNED: 'Returned',
        }

        # Copy dictionary so that we can change the copy safely
        btn_classes = alert_classes.copy()
        btn_classes[Rental.STATE_RETURNED] = 'primary'

        return render(request, 'rental/detail.html', {
            'rental': rental,
            'managed_by_user': managed_by_user,
            'states': states,
            'alert_classes': alert_classes,
            'btn_texts': btn_texts,
            'btn_classes': btn_classes,
        })
