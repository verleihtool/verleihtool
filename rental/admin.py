from django.contrib import admin
from .models import Rental, ItemRental


class ItemRentalInline(admin.TabularInline):
    model = ItemRental
    extra = 0


class RentalAdmin(admin.ModelAdmin):
    inlines = [ItemRentalInline]

    list_display = ['uuid', 'state']
    ordering = ['uuid']

    actions = ['make_approved', 'make_declined', 'make_pending', 'make_revoked']

    @staticmethod
    def format_message(num_changed, change):
        if num_changed == 1:
            message = "1 rental was"
        else:
            message = "%s rentals were" % num_changed
        return "%s successfully marked as %s" % (message, change)

    def make_approved(self, request, queryset):
        rentals_approved = queryset.update(state=Rental.STATE_APPROVED)
        self.message_user(request, RentalAdmin.format_message(rentals_approved, "approved"))
    make_approved.short_description = "Approve selected rentals"

    def make_declined(self, request, queryset):
        rentals_declined = queryset.update(state=Rental.STATE_DECLINED)
        self.message_user(request, RentalAdmin.format_message(rentals_declined, "declined"))
    make_declined.short_description = "Decline selected rentals"

    def make_pending(self, request, queryset):
        rentals_pending = queryset.update(state=Rental.STATE_PENDING)
        self.message_user(request, RentalAdmin.format_message(rentals_pending, "pending"))
    make_pending.short_description = "Mark selected rentals as pending"

    def make_revoked(self, request, queryset):
        rentals_revoked = queryset.update(state=Rental.STATE_REVOKED)
        self.message_user(request, RentalAdmin.format_message(rentals_revoked, "revoked"))
    make_revoked.short_description = "Revoke selected rentals"


# Register your models here.
admin.site.register(Rental, RentalAdmin)
