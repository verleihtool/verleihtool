from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.translation import ugettext_lazy as _


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

    name = models.CharField(max_length=32)
    groups = models.ManyToManyField(Group, blank=True)
    managers = models.ManyToManyField(User, blank=True)

    def managed_by(self, user):
        """
        Organizations are managed by superusers and organization managers.
        """

        return user.is_superuser or self.managers.filter(id=user.id).exists()

    def is_member(self, user):
        """
        Checks if the user is in one of the groups defined in this organization.
        """

        return self.groups.filter(id__in=user.groups.all()).exists()

    @property
    def active_depots(self):
        """
        Returns all depots in this organization which have the active flag set.
        """

        return self.depot_set.filter(active=True)

    @staticmethod
    def filter_by_user(user):
        """
        Filter for organizations managed by the given user
        """

        return models.Q(managers__id=user.id)

    def __str__(self):
        return self.name


class Depot(models.Model):
    """
    A depot has a name and many depot managers.

    :author: Leo Tappe
    :author: Benedikt Seidl
    """

    name = models.CharField(max_length=32)
    description = models.CharField(max_length=256, blank=True)
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

    def show_internal_items(self, user):
        """
        Internal items can be seen by superusers and organization members.
        """

        return user.is_superuser or self.organization.is_member(user)

    def visible_items(self, user):
        """
        Return the list of items the user is allowed to see in this depot.
        """

        if self.show_internal_items(user):
            return self.active_items.all()
        else:
            return self.public_items.all()

    @property
    def managers(self):
        """
        The list of users explicitly listed as managers of this depot.
        Does not include any organization managers or superusers which are
        not added to the depot.
        """

        return User.objects.filter(
            models.Q(id__in=self.manager_users.all()) |
            models.Q(groups__in=self.manager_groups.all())
        ).distinct()

    @property
    def public_items(self):
        """
        List all items with the visibility set to public.
        """

        return self.item_set.filter(visibility=Item.VISIBILITY_PUBLIC)

    @property
    def active_items(self):
        return self.item_set.filter(
            models.Q(visibility=Item.VISIBILITY_PUBLIC) |
            models.Q(visibility=Item.VISIBILITY_INTERNAL)
        )

    @staticmethod
    def filter_by_user(user):
        """
        Filter for depots managed by the given user
        """

        return (models.Q(organization__managers__id=user.id) |
                models.Q(manager_users__id=user.id) |
                models.Q(manager_groups__id__in=user.groups.all()))

    def __str__(self):
        return self.name


class Item(models.Model):
    """
    An item describes one or more instances of an object in a depot.

    It always belongs to a single depot and has a unique name within the depot.
    The location field can be used to roughly describe where
    the item can be found in the depot.
    Items can either be public or internal which affects the visibility
    of the item to users outside of the organization connected to the depot.
    The quantity describes how many version of the item exist in the depot.

    :author: Leo Tappe
    """

    VISIBILITY_PUBLIC = '1'
    VISIBILITY_INTERNAL = '2'
    VISIBILITY_DELETED = '3'
    VISIBILITY_LEVELS = (
        (VISIBILITY_PUBLIC, _('public')),
        (VISIBILITY_INTERNAL, _('internal')),
        (VISIBILITY_DELETED, _('deleted')),
    )

    name = models.CharField(max_length=32)
    description = models.CharField(max_length=1024, blank=True)
    quantity = models.PositiveSmallIntegerField()
    visibility = models.CharField(max_length=1, choices=VISIBILITY_LEVELS)
    location = models.CharField(max_length=256, blank=True)
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE)
    wikidata_item = models.CharField(max_length=32, blank=True, editable=False)

    @staticmethod
    def filter_by_user(user):
        """
        Filter for items managed by the given user
        """

        return (models.Q(depot__organization__managers__id=user.id) |
                models.Q(depot__manager_users__id=user.id) |
                models.Q(depot__manager_groups__id__in=user.groups.all()))

    class Meta:
        unique_together = (
            ('name', 'depot'),
        )

    def __str__(self):
        return self.name
