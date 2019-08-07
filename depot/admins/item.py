from depot.models import Depot, Item
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin


class ItemAdmin(TranslationAdmin):
    """
    Admin interface for items

    :author: Benedikt Seidl
    """

    list_display = ['name', 'quantity', 'visibility', 'location', 'depot']
    list_filter = [
        ('depot', admin.RelatedOnlyFieldListFilter),
        'visibility',
    ]
    ordering = ['name']

    # Custom admin actions
    actions = ['make_public', 'make_internal', 'make_deleted']

    def format_message(self, num_changed, change):
        if num_changed == 1:
            message = '1 item was'
        else:
            message = '%s items were' % num_changed
        return '%s successfully %s' % (message, change)

    def make_public(self, request, queryset):
        items_made_public = queryset.update(visibility=Item.VISIBILITY_PUBLIC)
        self.message_user(request, self.format_message(items_made_public, 'made public'))

    make_public.short_description = 'Mark selected items as public'

    def make_internal(self, request, queryset):
        items_made_internal = queryset.update(visibility=Item.VISIBILITY_INTERNAL)
        self.message_user(request, self.format_message(items_made_internal, 'made internal'))

    make_internal.short_description = 'Mark selected items as internal'

    def make_deleted(self, request, queryset):
        items_deleted = queryset.update(visibility=Item.VISIBILITY_DELETED)
        self.message_user(request, self.format_message(items_deleted, 'deleted'))

    make_deleted.short_description = 'Mark selected items as deleted'

    # Limit the accessible items to the one managed by the current user

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(Item.filter_by_user(request.user)).distinct()

    def has_add_permission(self, request):
        return (request.user.is_superuser
                or request.user.organization_set.exists()
                or request.user.depot_set.exists())

    def has_change_permission(self, request, obj=None):
        if not obj:
            return self.get_queryset(request).exists()

        return obj.depot.managed_by(request.user)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action from dropdown
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']

        return actions

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj, **kwargs)

        # Limit depot selection to the ones the current user is managing
        if not request.user.is_superuser and 'depot' in form.base_fields:
            form.base_fields['depot'].queryset = Depot.objects.filter(
                Depot.filter_by_user(request.user)
            ).distinct()

        return form
