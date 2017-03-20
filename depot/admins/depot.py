from depot.models import Depot, Item
from django.contrib import admin
from django.db.models import Q


# show items in depot
class ItemsInline(admin.TabularInline):
    model = Item
    extra = 0


class DepotAdmin(admin.ModelAdmin):
    inlines = [ItemsInline]
    list_display = ['name', 'active']
    ordering = ['name']

    actions = ["make_archived", "make_restored"]

    def format_message(self, num_changed, change):
        if num_changed == 1:
            message = "1 depot was"
        else:
            message = "%s depots were" % num_changed
        return "%s successfully marked as %s" % (message, change)

    def make_archived(self, request, queryset):
        depots_archived = queryset.update(active=False)
        self.message_user(request, self.format_message(depots_archived, "archived"))
    make_archived.short_description = "Archive selected depots"

    def make_restored(self, request, queryset):
        depots_restored = queryset.update(active=True)
        self.message_user(request, self.format_message(depots_restored, "restored"))
    make_restored.short_description = "Restore selected depots"

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(Q(manager_users__id=request.user.id) |
                         Q(manager_groups__id__in=request.user.groups.all()))

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True

        return False

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True

        if request.user.is_superuser:
            return True

        return obj.managed_by(request.user)

    def has_delete_permission(self, request, obj=None):
        return False
