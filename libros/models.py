from django.db import models
from users.models import User, Membresia
from perfiles.models import Perfil
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator

from datetime import date, datetime

class Genero(models.Model):
    nombre = models.CharField(max_length=50, unique=True)


    def __str__(self):
        return self.nombre


class Autor(models.Model):
    nombre = models.CharField(primary_key=True, unique=True, max_length=50)

    class Meta:
        verbose_name_plural = "autores"

    def __str__(self):
        return self.nombre

class Editorial(models.Model):

    nombre = models.CharField(primary_key=True, max_length=50)
    class Meta:
        verbose_name_plural = "editoriales"
    def __str__(self):
        return self.nombre

def validateDivision(value):

    libro = Libro.objects.get(id=value)
    if (libro.documento):
        raise ValidationError('Este libro no está disponible para agregarle capítulos. '
                              'Para realizar esta operación, usted debería eliminar el documento existente en el libro seleccionado.')
    elif libro.cantidad_partes == len(Capitulo.objects.filter(libro=libro.id)) :
        raise ValidationError('Este libro ya superó la cantidad de partes permitidas')
    else:
        return value

def validatePDF(value):
    ext = str(value).split('.')
    if ext[len(ext)-1] != 'pdf':
        raise ValidationError('El documento ingresado no es válido. Solo se permiten archivos con extensión ".pdf"')
    else:
        return value

def validateDate(value):
    if value < date.today():
        raise ValidationError('La fecha no puede ser menor que la actual.')
    else:
        return value

class Libro(models.Model):

    ISBN = models.BigIntegerField(unique=True)
    titulo = models.CharField(max_length=50)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    sinopsis = models.TextField()
    editorial = models.ForeignKey(Editorial, on_delete=models.CASCADE, null=True)
    genero = models.ManyToManyField(Genero)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lanzamiento_basico = models.DateField(null=True, blank=True)
    fecha_lanzamiento_premium = models.DateField(null=True, blank=True)
    fecha_vencimiento_basico = models.DateField(null=True, blank=True)
    fecha_vencimiento_premium = models.DateField(null=True, blank=True)
    cantidad_partes = models.IntegerField(null=True, default=1)
    documento = models.FileField(null=True, blank=True, validators=[validatePDF])
    imagen = models.ImageField(null=True, default='no_load.jpg')
    exclusividad = models.ForeignKey(Membresia, on_delete=models.CASCADE, null=True)
    class Meta:
        verbose_name_plural = "libros"

    def __str__(self):
        return self.titulo

def getLib(value):
    return Libro.objects.get(id=value)

class Capitulo(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, validators=[validateDivision])
    titulo = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True)
    indice = models.IntegerField()
    texto = models.FileField(validators=[validatePDF])
    imagen = models.ImageField(null=True, blank=True)
    fecha_lanzamiento_basico = models.DateField(null=True, validators=[validateDate])
    fecha_lanzamiento_premium = models.DateField(null=True, validators=[validateDate])
    fecha_vencimiento_basico = models.DateField(null=True, blank=True, validators=[validateDate])
    fecha_vencimiento_premium = models.DateField(null=True, blank=True)
    exclusividad = models.ForeignKey(Membresia, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (['libro', 'titulo'], ['libro', 'indice'])
    def __str__(self):
        return self.titulo


class LibroLeido(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, null=True, blank=True)
    cap = models.ForeignKey(Capitulo, on_delete=models.CASCADE, null=True, blank=True)
    pagina = models.IntegerField(default=0)
    ultima_fecha = models.DateField(auto_now=True)
    terminado = models.BooleanField(default=True)

    class Meta:
        unique_together = (['perfil', 'libro'], ['perfil', 'cap'])

    def __str__(self):
        if self.libro:
            return self.libro.titulo
        return self.cap.titulo



class Calificacion(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    valor = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('libro', 'perfil')
        verbose_name_plural = "calificaciones"

    def __str__(self):
        return str(self.valor)

class Comentario(models.Model):
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, null=True, blank=True)
    spoiler = models.BooleanField(default=False)
    valor = models.ForeignKey(Calificacion, on_delete=models.CASCADE, null=True, blank=True)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if len(self.texto) > 50:
            frase = self.texto[:50] + "..."
        else:
            frase = self.texto
        return frase

    class Meta:
        verbose_name_plural = 'comentarios'

class ReporteSpoiler(models.Model):
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE)
    reportador = models.ForeignKey(Perfil, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "reportes de spoilers"

class ReporteOfensivo(models.Model):
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE)
    reportador = models.ForeignKey(Perfil, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "reportes de comentarios ofensivos"


class LibroMinuscula(models.CharField):
    def __init__(self, *args, **kwargs):
        super(LibroMinuscula, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).lower()


class LibroSugerido(models.Model):
    perfiles = models.ManyToManyField(Perfil)
    sugerencia = LibroMinuscula(max_length=40, blank=True)

    class Meta:
        verbose_name_plural = "libros sugeridos"

    def __str__(self):
        return self.sugerencia

