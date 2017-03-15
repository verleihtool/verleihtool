from django.contrib import admin
from .models import Depot, Item


# show items in depot
class ItemsInline(admin.TabularInline):
    model = Item
    extra = 0


class DepotAdmin(admin.ModelAdmin):
    inlines = [ItemsInline]
    list_display = ['name', 'active']
    ordering = ['name']

    actions = ["make_archived", "make_restored"]

    @staticmethod
    def format_message(num_changed, change):
        if num_changed == 1:
            message = "1 depot was"
        else:
            message = "%s depots were" % num_changed
        return "%s successfully marked as %s" % (message, change)

    def make_archived(self, request, queryset):
        depots_archived = queryset.update(active=False)
        self.message_user(request, DepotAdmin.format_message(depots_archived, "archived"))
    make_archived.short_description = "Archive selected depots"

    def make_restored(self, request, queryset):
        depots_restored = queryset.update(active=True)
        self.message_user(request, DepotAdmin.format_message(depots_restored, "restored"))
    make_restored.short_description = "Restore selected depots"


# make items modifiable by admin
admin.site.register(Item)

# make depots modifiable by admin
admin.site.register(Depot, DepotAdmin)
