from django.db import models
from django.contrib.auth.models import Group, User


class Organization(models.Model):
    """
    Model an organization, such as FSMPI, FSMB or ASTA.

    An organization is defined by a list of user groups,
    in our case LDAP groups. It is managed by a list of
    users and has a list of depots.

    :author: Leo Tappe
    """

    name = models.CharField(max_length=256)
    groups = models.ManyToManyField(Group)
    managers = models.ManyToManyField(User)

    def __str__(self):
        return 'Organization %s' % self.name


class Depot(models.Model):
    """
    Model a depot.
    A depot has a name and many depot managers.

    :author: Leo Tappe
    """
    name = models.CharField(max_length=256)
    organization = models.ForeignKey(Organization)
    manager_users = models.ManyToManyField(User, blank=True)
    manager_groups = models.ManyToManyField(Group, blank=True)
    active = models.BooleanField(default=True)

    def managed_by(self, user):
        return (self.manager_users.filter(id=user.id).exists() or
                self.manager_groups.filter(id__in=user.groups.all()).exists())

    @property
    def managers(self):
        return User.objects.filter(
            models.Q(id__in=self.manager_users.all()) |
            models.Q(groups__in=self.manager_groups.all())
        )

    def __str__(self):
        return 'Depot %s' % self.name


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
    quantity = models.PositiveSmallIntegerField()
    visibility = models.CharField(max_length=1, choices=VISIBILITY_LEVELS)
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE)
    location = models.CharField(max_length=256)

    def __str__(self):
        return ('%s unit(s) of %s (visib.: %s) in %s'
                % (self.quantity, self.name, self.visibility, self.location))
