from django.db import models
from django.contrib.auth.models import Group, User


class Organization(models.Model):
    """
    Representation of an organization,
    such as FSMPI, FSMB or ASTA.

    An organization is defined by a list of user groups,
    in our case LDAP groups. It is managed by a list of
    users and has a list of depots.

    :author: Leo Tappe
    :author: Benedikt Seidl
    """

    name = models.CharField(max_length=256)
    groups = models.ManyToManyField(Group)
    managers = models.ManyToManyField(User)

    def managed_by(self, user):
        """
        Organizations are managed by superusers and organization managers.
        """

        return user.is_superuser or self.managers.filter(id=user.id).exists()

    def is_member(self, user):
        return self.groups.filter(id__in=user.groups.all()).exists()

    @property
    def active_depots(self):
        return self.depot_set.filter(active=True)

    def __str__(self):
        return 'Organization %s' % self.name


class Depot(models.Model):
    """
    A depot has a name and many depot managers.

    :author: Leo Tappe
    :author: Benedikt Seidl
    """

    name = models.CharField(max_length=256)
    organization = models.ForeignKey(Organization)
    manager_users = models.ManyToManyField(User, blank=True)
    manager_groups = models.ManyToManyField(Group, blank=True)
    active = models.BooleanField(default=True)

    def managed_by(self, user):
        """
        Depots are managed by superusers, the organization's managers,
        any manager user and any user in a manager group.
        """

        return (user.is_superuser or
                self.organization.managed_by(user) or
                self.manager_users.filter(id=user.id).exists() or
                self.manager_groups.filter(id__in=user.groups.all()).exists())

    @property
    def managers(self):
        return User.objects.filter(
            models.Q(id__in=self.manager_users.all()) |
            models.Q(groups__in=self.manager_groups.all())
        )

    @property
    def public_items(self):
        return self.item_set.filter(visibility=Item.VISIBILITY_PUBLIC)

    def __str__(self):
        return 'Depot %s' % self.name


class Item(models.Model):
    """
    An item describes one or more instances of an object in a depot.

    It always belongs to a single depot and has a unique name within the depot.
    The location field can be used to roughly describe where
    the item can be found in the depot.
    Items can either be public or private which affects the visibility
    of the item to users outside of the organization connected to the depot.
    The quantity describes how many version of the item exist in the depot.

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

    class Meta:
        unique_together = (
            ('name', 'depot'),
        )

    def __str__(self):
        return ('%s unit(s) of %s (visib.: %s) in %s'
                % (self.quantity, self.name, self.visibility, self.location))
