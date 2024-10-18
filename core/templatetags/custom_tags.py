from django import template

register = template.Library()

@register.filter
def is_supervisor(user):
    return user.groups.filter(name='supervisores').exists()
