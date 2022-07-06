from django import template

register = template.Library()


@register.filter(name='range')
def create_range(times: int):
    return range(times)
