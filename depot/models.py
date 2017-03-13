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
    active = models.BooleanField(default=True)

    def __str__(self):
        return "Depot %s" % self.name

class Item(models.Model):
    """
    Model an item.
    An item has a name.
    Quantity: how many versions of this item exist.
    An item has different visibility levels, which determine who can view them.
    An item is in a depot.
    An item has a specific location within its depot.

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
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE)
    location = models.CharField(max_length=256)

    def __str__(self):
        return ('%s unit(s) of %s (visib.: %s) in %s'
                % (self.quantity, self.name, self.visibility, self.location))
