from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    
    return d.get(key)

@register.filter
def abs_value(value):
    """Return the absolute value of a number."""
    return abs(value)