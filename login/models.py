from django.contrib.auth import signals
from django.contrib.auth.models import Permission


def on_user_logged_in(sender, user, request, **kwargs):
    """
    Add all permissions for the models we created to the user.

    :author: Benedikt Seidl
    """

    permissions = Permission.objects.filter(
        content_type__app_label__in=['depot', 'rental'],
        content_type__model__in=[
            'depot', 'item', 'organization', 'rental', 'itemrental'
        ]
    )

    user.user_permissions.set(permissions)


signals.user_logged_in.connect(on_user_logged_in)
