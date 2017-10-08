import uuid
from datetime import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from depot.models import Depot, Item


class Rental(models.Model):
    """
    A rental defines the amount of items and has a start and return date.
    Only items from one depot can be requested for rental at once.

    When requesting a rental, the user has to enter his full name and email
    address as well as describing the purpose of his rental. If they are
    logged in, the user's id will be stored as well.

    After creating a rental request, it is in the PENDING state. From this,
    it can be either APPROVED or DECLINED by a depot manager or REVOKED by
    the requesting user. If all items were returned correctly, it can be
    set to RETURNED to finish the rental process.

    :author: Benedikt Seidl
    """

    STATE_PENDING = '1'
    STATE_APPROVED = '2'
    STATE_DECLINED = '3'
    STATE_REVOKED = '4'
    STATE_RETURNED = '5'
    STATES = (
        (STATE_PENDING, 'pending'),
        (STATE_APPROVED, 'approved'),
        (STATE_DECLINED, 'declined'),
        (STATE_REVOKED, 'revoked'),
        (STATE_RETURNED, 'returned'),
    )

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    depot = models.ForeignKey(Depot)
    items = models.ManyToManyField(Item, through='ItemRental')
    firstname = models.CharField(max_length=256)
    lastname = models.CharField(max_length=256)
    email = models.EmailField()
    purpose = models.CharField(max_length=256)
    user = models.ForeignKey(User, blank=True, null=True)
    start_date = models.DateTimeField()
    return_date = models.DateTimeField()
    state = models.CharField(max_length=1, choices=STATES, default=STATE_PENDING)

    def clean(self):
        if not self.depot.active:
            raise ValidationError({'depot': 'The depot has to be active.'})

        if self.start_date > self.return_date:
            raise ValidationError({
                'start_date': 'The start date must be before the return date.'
            })

        if self.start_date < datetime.now() and self.state == self.STATE_PENDING:
            raise ValidationError({
                'start_date': 'The start date must be in the future for new rentals.'
            })

    def __str__(self):
        return 'Rental by %s %s' % (self.firstname, self.lastname)


class ItemRental(models.Model):
    """
    Intermediate relationship for each item within a rental.
    Defines the quantity and number of returned items.

    :author: Benedikt Seidl
    """

    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    returned = models.PositiveSmallIntegerField(default=0)

    def clean(self):
        if self.rental.depot_id != self.item.depot_id:
            raise ValidationError({
                'item': 'The item must come from the depot the rental was created for.'
            })

        if self.item.visibility != Item.VISIBILITY_PUBLIC:
            organization = self.rental.depot.organization
            user = self.rental.user

            if user is None or not organization.is_member(user):
                raise ValidationError({
                    'item': 'You have to be a member of the organization '
                            'that manages this depot to rent a private item.'
                })

        if self.quantity <= 0 or self.quantity > self.item.quantity:
            raise ValidationError({
                'quantity': 'The quantity must be positive and less than or '
                            'equal to the total amount of available items.'
            })

        if self.returned > self.quantity:
            raise ValidationError({
                'returned': 'The amount of returned items must be less than or '
                            'equal to the total amount of rented items.'
            })
