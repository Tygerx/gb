from django import template

register = template.Library()

@register.filter
def distinct(queryset, field):
    """Returns distinct values for a given field in a queryset"""
    return list(set(getattr(item, field) for item in queryset))

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def add(value, arg):
    """Adds the argument to the value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return '' 