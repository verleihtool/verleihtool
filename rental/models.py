import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from depot.models import Item


class Rental(models.Model):
    """
    A rental defines the amount of items and has a start and return date.

    :author: Benedikt Seidl
    """

    STATE_PENDING = '1'
    STATE_APPROVED = '2'
    STATE_DECLINED = '3'
    STATE_REVOKED = '4'
    STATES = (
        (STATE_PENDING, 'pending'),
        (STATE_APPROVED, 'approved'),
        (STATE_DECLINED, 'declined'),
        (STATE_REVOKED, 'revoked'),
    )

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    items = models.ManyToManyField(Item, through='ItemRental')
    name = models.CharField(max_length=256)
    email = models.EmailField()
    purpose = models.CharField(max_length=256, blank=True)
    user = models.ForeignKey(User, blank=True, null=True)
    start_date = models.DateTimeField()
    return_date = models.DateTimeField()
    state = models.CharField(max_length=1, choices=STATES, default=STATE_PENDING)

    def clean(self):
        if self.start_date > self.return_date:
            raise ValidationError({'start_date': 'The start date must be before the return date.'})

    def __str__(self):
        return 'Rental by %s' % self.name


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
