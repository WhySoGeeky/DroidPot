__author__ = 'droid'
from django import template

register = template.Library()

@register.filter(is_safe=True)
def replace_underscore(value):
    """
    convert string with underscore to space
    :param value:
    :return:
    """
    return value.replace("_", " ")