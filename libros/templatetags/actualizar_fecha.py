from django import template
from libros.models import LibroLeido
register = template.Library()


libro = LibroLeido
@register.simple_tag
def actualizar_f(fecha):
    return fecha
