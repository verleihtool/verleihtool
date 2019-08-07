import json
from django import template
from django.urls import translate_url
from depot.models import Item
from rental.models import Rental


register = template.Library()


@register.simple_tag(takes_context=True)
def current_app(context, app_name, content):
    """
    If the current page belongs to the given app, then return the given content.

    :author: Benedikt Seidl
    """

    current_app_name = context['request'].resolver_match.app_names[0]
    if app_name == current_app_name:
        return content


@register.simple_tag(takes_context=True)
def base_url(context):
    return context['request'].build_absolute_uri('/')[:-1]


@register.simple_tag(takes_context=True)
def change_lang(context, lang):
    path = context['request'].path

    return translate_url(path, lang)


@register.simple_tag
def item_visibility(visibility):
    """
    Turn the given visibility into a readable string.

    :author: Florian Stamer
    """

    return dict(Item.VISIBILITY_LEVELS)[visibility]


@register.simple_tag
def item_visibility_glyphicon(visibility):
    """
    Provide a glyphicon for the given item visibility.

    :author: Benedikt Seidl
    """

    glyphicons = {
        Item.VISIBILITY_PUBLIC: 'eye-open',
        Item.VISIBILITY_INTERNAL: 'eye-close',
        Item.VISIBILITY_DELETED: 'trash',
    }

    return glyphicons[visibility]


@register.simple_tag
def rental_state(state):
    """
    Turn the given state into a readable string.

    :author: Florian Stamer
    """

    return dict(Rental.STATES)[state]


@register.simple_tag
def rental_state_class(state):
    """
    Provide a bootstrap contextual class for each rental state.

    :author: Benedikt Seidl
    """

    bootstrap_classes = {
        Rental.STATE_PENDING: 'warning',
        Rental.STATE_REVOKED: 'danger',
        Rental.STATE_APPROVED: 'success',
        Rental.STATE_DECLINED: 'danger',
        Rental.STATE_RETURNED: 'info',
    }

    return bootstrap_classes[state]


@register.simple_tag
def concat_with_and(list, final='and', empty=''):
    """
    Concatenate the given list to a string separated with commas
    and final concatenator (default "and")

    :author: Benedikt Seidl
    """

    if not list:
        return empty

    if len(list) == 1:
        return list[0]

    return '%s %s %s' % (
        ', '.join(str(item) for item in list[:-1]),
        final,
        str(list[-1])
    )


@register.filter
def key(dictionary, key):
    """
    Return the appropriate label for the given state

    :author: Florian Stamer
    """

    return dictionary.get(key)


@register.filter
def tojson(object):
    """
    Turn the given object into its JSON representation

    :author: Benedikt Seidl
    """

    return json.dumps(object)


@register.filter
def full_name(user):
    """
    Return first and last name of the user if available

    :author: Benedikt Seidl
    """

    if user.first_name and user.last_name:
        return '%s %s' % (user.first_name, user.last_name)
    else:
        return user.username


@register.filter
def full_names(users):
    """
    Turn the given user list into a list of full names

    :author: Benedikt Seidl
    """

    return list(map(full_name, users))
