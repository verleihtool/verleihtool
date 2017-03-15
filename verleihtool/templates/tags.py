from django import template
from django.http import request


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
