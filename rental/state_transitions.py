from .models import Rental


def allowed_transitions(managed_by_user, current_state):
    """
    Return the list of valid transitions from the current state
    based on the user's permissions

    :author: Benedikt Seidl
    """

    if managed_by_user:
        return STATE_TRANSITIONS_MANAGER[current_state]
    else:
        return STATE_TRANSITIONS_USER[current_state]


# Allowed state transitions for managers of the connected depot
STATE_TRANSITIONS_MANAGER = {
    Rental.STATE_PENDING: [
        Rental.STATE_REVOKED,
        Rental.STATE_APPROVED,
        Rental.STATE_DECLINED,
    ],
    Rental.STATE_REVOKED: [
        Rental.STATE_PENDING,
    ],
    Rental.STATE_APPROVED: [
        Rental.STATE_PENDING,
        Rental.STATE_REVOKED,
        Rental.STATE_DECLINED,
        Rental.STATE_RETURNED,
    ],
    Rental.STATE_DECLINED: [
        Rental.STATE_PENDING,
        Rental.STATE_APPROVED,
    ],
    Rental.STATE_RETURNED: [
        Rental.STATE_APPROVED,
    ]
}

# Allowed state transitions for any other user
STATE_TRANSITIONS_USER = {
    Rental.STATE_PENDING: [
        Rental.STATE_REVOKED,
    ],
    Rental.STATE_REVOKED: [
        Rental.STATE_PENDING,
    ],
    Rental.STATE_APPROVED: [
        Rental.STATE_REVOKED,
    ],
    Rental.STATE_DECLINED: [],
    Rental.STATE_RETURNED: [],
}
