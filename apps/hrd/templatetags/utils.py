from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(int(key))

@register.filter
def to_list(start, end):
    return range(start, end + 1)
