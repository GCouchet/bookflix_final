from django.db import models
from libros.models import Libro
# Create your models here.

class Novedad(models.Model):
    titulo = models.CharField(unique=True, null=False, max_length=100)
    descripcion = models.CharField(null=False, max_length=1000)
    libro = models.OneToOneField(Libro, null=True, on_delete=models.CASCADE, blank=True)
    fechaLanzamiento = models.DateField(null=False)
    fechaExpiracion = models.DateField(null=False)
    imagen = models.ImageField(null=True, blank=True)
    descripcion_imagen = models.CharField(null=True, max_length=1000, blank=True)
    trailer = models.CharField(max_length=50, null=True, help_text='Nota: Utilice el formato http://www.tupagina.com/ para asignar una url externa al sitio.', blank=True)

    class Meta:
        verbose_name_plural = "novedades"
    def __str__(self):
        return self.titulo