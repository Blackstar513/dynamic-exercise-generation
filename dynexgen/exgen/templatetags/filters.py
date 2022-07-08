from django import template

register = template.Library()


@register.filter(name='range')
def create_range(times: int):
    return range(times)


@register.filter(name='index')
def get_at_index(indexable, i):
    return indexable[i]