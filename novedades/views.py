from django.shortcuts import render
from .models import Novedad
from datetime import date
from libros.models import Libro
from django.db.models import Q
from libros.views import verificateUser

def extendsContext(request, tmpDict):
    tmpTrailer = Novedad.objects.filter(Q(libro__isnull=False) | Q(trailer__isnull=False)).order_by('?')
    tmpTrailers = filter(lambda x : x.fechaLanzamiento <= date.today()  and x.fechaExpiracion > date.today(), tmpTrailer )
    contexto = { 'trailer': tmpTrailers }
    return {**contexto, **tmpDict}


def index(request):

    def books_for_basic(bookslsts):
        bookslsts = filter(lambda x : x.exclusividad.nombre == 'Básico', bookslsts)
        bookslsts = list(filter(lambda x: x.fecha_lanzamiento_basico <= date.today(), bookslsts))
        return list(bookslsts)

    novs = Novedad.objects.filter(libro__isnull=True, trailer__isnull=True).order_by('fechaLanzamiento').reverse()[0:3]
    novss = filter(lambda x : x.fechaLanzamiento <= date.today()  and x.fechaExpiracion > date.today(), novs )
    bookslsts = Libro.objects.order_by('fecha_creacion').reverse()
    if request.user.is_authenticated:
        if not request.user.is_staff:
            if request.user.subscription.nombre == 'Básico':
                bookslsts = books_for_basic(bookslsts)
            else:
                premium = Libro.objects.filter(exclusividad=2)
                premium = list(filter(lambda x:(x.fecha_lanzamiento_premium is None) or (x.fecha_lanzamiento_premium <= date.today()), premium))
                books = premium + books_for_basic(bookslsts)
                bookslsts = list(filter(lambda x: (x.fecha_vencimiento_premium is None) or (x.fecha_vencimiento_premium > date.today()), books))

    context = extendsContext(request, {'novedades': novss, 'libros': list(bookslsts)[0:6]})
    return render(request, 'index.html', context)

@verificateUser
def novedades(request):
    novs = Novedad.objects.filter(libro__isnull=True, trailer__isnull=True).order_by('fechaLanzamiento').reverse()
    novss = filter(lambda x : x.fechaLanzamiento <= date.today() and x.fechaExpiracion > date.today(), novs )
    context = {'novedades': novss}
    return render(request, 'listado_novedades.html', context)

@verificateUser
def trailers(request):
    novs = Novedad.objects.filter(Q(libro__isnull=False) | Q(trailer__isnull=False)).order_by('fechaLanzamiento').reverse()
    novss = filter(lambda x : x.fechaLanzamiento <= date.today() and x.fechaExpiracion > date.today(), novs )
    context = {'novedades': novss}
    return render(request, 'listado_trailers.html', context)

@verificateUser
def novedad(request, novedad_id):
    nov = Novedad.objects.get(id=novedad_id)
    lib = nov.libro
    context =  {'novedad' : nov, 'libro': lib}
    return render(request, 'novedad.html', context)