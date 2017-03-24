from django.contrib import admin
from .models import Rental, ItemRental
from django.db.models import Q


class ItemRentalInline(admin.TabularInline):
    model = ItemRental
    extra = 0


class RentalAdmin(admin.ModelAdmin):
    inlines = [ItemRentalInline]

    list_display = ['uuid', 'lastname', 'firstname', 'email', 'state']
    ordering = ['uuid']

    actions = ['make_approved', 'make_declined', 'make_pending', 'make_revoked']

    @staticmethod
    def format_message(num_changed, change):
        if num_changed == 1:
            message = '1 rental was'
        else:
            message = '%s rentals were' % num_changed
        return '%s successfully marked as %s' % (message, change)

    def make_approved(self, request, queryset):
        rentals_approved = queryset.update(state=Rental.STATE_APPROVED)
        self.message_user(request, RentalAdmin.format_message(rentals_approved, 'approved'))
    make_approved.short_description = 'Approve selected rentals'

    def make_declined(self, request, queryset):
        rentals_declined = queryset.update(state=Rental.STATE_DECLINED)
        self.message_user(request, RentalAdmin.format_message(rentals_declined, 'declined'))
    make_declined.short_description = 'Decline selected rentals'

    def make_pending(self, request, queryset):
        rentals_pending = queryset.update(state=Rental.STATE_PENDING)
        self.message_user(request, RentalAdmin.format_message(rentals_pending, 'pending'))
    make_pending.short_description = 'Mark selected rentals as pending'

    def make_revoked(self, request, queryset):
        rentals_revoked = queryset.update(state=Rental.STATE_REVOKED)
        self.message_user(request, RentalAdmin.format_message(rentals_revoked, 'revoked'))
    make_revoked.short_description = 'Revoke selected rentals'

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        # ugliest query alive
        return qs.filter(Q(depot__manager_users__id=request.user.id) |
                         Q(depot__manager_groups__id__in=request.user.groups.all()))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True

        if request.user.is_superuser:
            return True

        return obj.depot.managed_by(request.user)

    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
admin.site.register(Rental, RentalAdmin)
