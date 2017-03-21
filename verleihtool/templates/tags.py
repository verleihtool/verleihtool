from django import template
from django.http import request
from depot.models import Item


register = template.Library()


@register.simple_tag(takes_context=True)
def current_page(context, path_name, content):
    """
    If the current page equals the path_name, then return the given content.

    :author: Benedikt Seidl
    """

    app_name = context['request'].resolver_match.app_names[0]
    url_name = context['request'].resolver_match.url_name
    if '%s:%s' % (app_name, url_name) == path_name:
        return content


@register.simple_tag
def item_visibility(visibility):
    """
    Turn the given visibility into a readable string.

    :author: Florian Stamer
    """

    return dict(Item.VISIBILITY_LEVELS)[visibility]


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
