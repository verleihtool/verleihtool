from depot.models import Depot
from django.contrib import admin


# show depots in organization
class DepotInline(admin.TabularInline):
    model = Depot
    extra = 0
    can_delete = False

    filter_vertical = ['manager_users', 'manager_groups']


class OrganizationAdmin(admin.ModelAdmin):
    """
    Admin interface for organizations

    Organizations can only created by superusers and changed by any
    manager of the organization. They cannot be deleted.

    :author: Leo Tappe
    """

    inlines = [DepotInline]
    filter_horizontal = ['groups', 'managers']

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(managers__id=request.user.id)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True

        return False

    def has_change_permission(self, request, obj=None):
        if not obj:
            return self.get_queryset(request).exists()

        return obj.managed_by(request.user)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action from dropdown
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']

        return actions
