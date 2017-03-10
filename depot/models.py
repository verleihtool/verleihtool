from django.db import models
from django.contrib.auth.models import Group, User

class Depot(models.Model):
    """
    Model a depot.
    A depot has a name and many depot managers.

    :author: Leo Tappe
    """
    name = models.CharField(max_length=256)
    managers = models.ManyToManyField(User)

class Item(models.Model):
    """
    Model an item.
    An item has a name.
    Quantity: how many versions of this item exist.
    An item has different visibility levels, which determine who can view them.
    An item has a specific location within a depot.

    :author: Leo Tappe
    """
    VISIBILITY_PUBLIC = '1'
    VISIBILITY_PRIVATE = '2'
    VISIBILITY_LEVELS = (
        (VISIBILITY_PUBLIC, 'public'),
        (VISIBILITY_PRIVATE, 'private'),
    )
    name = models.CharField(max_length=256)
    quantity = models.IntegerField()
    visibility = models.CharField(max_length=1, choices=VISIBILITY_LEVELS)
    location = models.CharField(max_length=256)
