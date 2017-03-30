from django.contrib import admin
from django.db.models import Q
from rental.models import Rental, ItemRental


class ItemRentalInline(admin.TabularInline):
    model = ItemRental
    extra = 0


class RentalAdmin(admin.ModelAdmin):
    """
    Admin interface for rentals

    Rentals can be approved, declined, revoked and marked as pending or returned.
    They are only accessible for the managers of the connected depot.

    TODO: This admin interface may be obsolete.

    :author: Benedikt Seidl
    :author: Leo Tappe
    """

    inlines = [ItemRentalInline]
    list_display = ['uuid', 'firstname', 'lastname', 'email', 'state']
    ordering = ['uuid']

    # Custom admin actions
    actions = ['make_approved', 'make_declined', 'make_pending', 'make_revoked', 'make_returned']

    def format_message(self, num_changed, change):
        if num_changed == 1:
            message = '1 rental was'
        else:
            message = '%s rentals were' % num_changed
        return '%s successfully marked as %s' % (message, change)

    def make_approved(self, request, queryset):
        rentals_approved = queryset.update(state=Rental.STATE_APPROVED)
        self.message_user(request, self.format_message(rentals_approved, 'approved'))

    make_approved.short_description = 'Approve selected rentals'

    def make_declined(self, request, queryset):
        rentals_declined = queryset.update(state=Rental.STATE_DECLINED)
        self.message_user(request, self.format_message(rentals_declined, 'declined'))

    make_declined.short_description = 'Decline selected rentals'

    def make_pending(self, request, queryset):
        rentals_pending = queryset.update(state=Rental.STATE_PENDING)
        self.message_user(request, self.format_message(rentals_pending, 'pending'))

    make_pending.short_description = 'Mark selected rentals as pending'

    def make_revoked(self, request, queryset):
        rentals_revoked = queryset.update(state=Rental.STATE_REVOKED)
        self.message_user(request, self.format_message(rentals_revoked, 'revoked'))

    make_revoked.short_description = 'Revoke selected rentals'

    def make_returned(self, request, queryset):
        rentals_returned = queryset.update(state=Rental.STATE_RETURNED)
        self.message_user(request, self.format_message(rentals_returned, 'returned'))

    make_revoked.short_description = 'Mark selected rentals as returned'

    # Limit access to rentals to the managers of the connected depots

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(Q(depot__organization__managers__id=request.user.id) |
                         Q(depot__manager_users__id=request.user.id) |
                         Q(depot__manager_groups__id__in=request.user.groups.all()))

    def has_add_permission(self, request):
        # Only via the rental request form
        return False

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True

        return obj.depot.managed_by(request.user)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action from dropdown
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']

        return actions

    def get_readonly_fields(self, request, obj=None):
        # The depot of a rental cannot be changed
        if obj:
            return ['depot']

        return []


# Register your models here.
admin.site.register(Rental, RentalAdmin)
