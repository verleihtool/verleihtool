from depot.models import Depot, Organization
from django.contrib import admin


class OrganizationAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        """
        Superusers can see every organization.
        Other users can see only the organizations which they manage.
        """
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(managers__id=request.user.id)

    def has_add_permission(self, request):
        """
        Only superusers can create new organizations.
        """
        if request.user.is_superuser:
            return True

        return False

    def has_change_permission(self, request, obj=None):
        """
        Only superusers and organization managers can change an organization.
        """
        if not obj:
            return True

        if request.user.is_superuser:
            return True

        if obj.managers.filter(id=request.user.id).exists():
            return True

        return False

    def has_delete_permission(self, request, obj=None):
        """
        Organizations can't be deleted.
        """
        return False
