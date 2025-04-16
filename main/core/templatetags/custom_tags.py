from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    
    return d.get(key)

@register.filter
def draft_position_diff(ranking, pick_number):
    """Calculate absolute difference between draft ranking and pick number."""
    try:
        return abs(int(ranking) - int(pick_number))
    except (ValueError, TypeError):
        return 0