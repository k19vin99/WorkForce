from django import template
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    """Agrega una clase CSS al widget de un campo de formulario."""
    if hasattr(value, 'field') and hasattr(value.field.widget, 'attrs'):
        existing_classes = value.field.widget.attrs.get('class', '')
        value.field.widget.attrs['class'] = f"{existing_classes} {css_class}".strip()
    return value

@register.filter
def is_supervisor(user):
    return user.groups.filter(name='supervisores').exists()

register = template.Library()

@register.filter
def get_bar_color(progreso):
    try:
        progreso = int(progreso)  # Convertir a entero
    except ValueError:
        return "#000000"  # Devuelve un color por defecto en caso de error

    if progreso < 25:
        return "#dc3545"  # Rojo
    elif progreso < 50:
        return "#ffc107"  # Amarillo
    elif progreso < 75:
        return "#0d6efd"  # Azul
    else:
        return "#28a745"  # Verde