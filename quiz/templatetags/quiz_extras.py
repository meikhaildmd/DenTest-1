# templatetags/quiz_extras.py

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Custom filter to get a value from a dictionary by key."""
    return dictionary.get(key)


@register.filter
def get_field(obj, field_name):
    """Custom filter to get an attribute from an object by name."""
    return getattr(obj, field_name)
