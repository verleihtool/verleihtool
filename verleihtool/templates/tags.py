import json
from django import template
from django.http import request
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
    return context['request'].build_absolute_uri('')


@register.simple_tag
def item_visibility(visibility):
    """
    Turn the given visibility into a readable string.

    :author: Florian Stamer
    """

    return dict(Item.VISIBILITY_LEVELS)[visibility]


@register.simple_tag
def rental_state(state):
    """
    Turn the geiven state into a readable string.

    :author: Florian Stamer
    """
    return dict(Rental.STATES)[state]


@register.simple_tag
def concat_with_and(list, final='and'):
    """
    Concatenate the given list to a string separated with commas
    and final concatenator (default "and")

    :author: Benedikt Seidl
    """

    if not list:
        return ''

    l = len(list)
    if l == 1:
        return list[0]

    return '%s %s %s' % (
        ', '.join(str(item) for item in list[:l - 1]),
        final,
        str(list[l - 1])
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
