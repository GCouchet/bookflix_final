from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Autor, Genero, Libro, Capitulo, Calificacion, Comentario, Editorial, LibroLeido, ReporteSpoiler, ReporteOfensivo, LibroSugerido
from .forms import LibroSugeridoForm
from perfiles. models import Perfil
from datetime import date, datetime
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView
import json

def verificateUser(funcion):
    def verificate(req, **kwargs):
        if not req.user.is_staff:
            if not req.user.is_authenticated:
                return redirect('users:login')
            else:
                if (not req.user.suspendida == None) and (req.user.is_suspended):
                    #return render(req, 'restrictions/suspendida.html')
                    messages.success(req, 'Su cuenta se encuentra suspendida por falta de pago. Por favor, regularice su situación.')
                    return redirect('users:logout')
                else:
                    if req.session['myProfile'] is None:                #profile = req.session.get['myProfile']
                        return redirect('perfiles:seleccionarPerfil')
                    else:
                        return funcion(req, **kwargs)
        else:
                    return funcion(req, **kwargs)
    return verificate


def get_pdf(pdfname):
    return str('/imagenes/' + str(pdfname)+'#toolbar=0&navpanes=0&scrollbar=0')

@verificateUser
def index(request):
    """Home page of library"""

    return render(request, 'index.html')

@verificateUser
def libros(request):
    """Show all books"""
    bookslsts = Libro.objects.order_by('fecha_creacion').reverse()
    if not request.user.is_staff:
        if not request.user.is_staff:
            if request.user.subscription.nombre == 'Básico':
                bookslst = list(filter(lambda x : x.exclusividad.nombre == 'Básico', bookslsts))
                bookslst = list(filter(lambda x: x.fecha_lanzamiento_basico <= date.today(), bookslst))
                bookspremium = list(filter(lambda x : x.exclusividad.nombre != 'Básico', bookslsts))
                books = list(filter(lambda x : x.fecha_lanzamiento_premium <= date.today(), bookspremium))
                bookslsts = bookslst + books

            else:
                books = filter(lambda x : x.fecha_lanzamiento_premium <= date.today(), bookslsts)
                bookslsts = filter(lambda x: x.fecha_vencimiento_premium > date.today(), books)

    context = {'books': bookslsts}
    return render(request, 'listado_libros.html', context)

@verificateUser
def libro(request, libro_isbn):
    bk = Libro.objects.get(ISBN=libro_isbn)
    my_calification = {}
    my_calification['valor'] = None
    my_calification['comentario'] = None
    calificacion = obtener_calificaciones(bk)
    chapters = Capitulo.objects.filter(libro=bk).order_by('num')
    if not request.user.is_staff:
        mi_perfil = Perfil.objects.get(id=request.session['myProfile'])
        if Calificacion.objects.filter(libro=bk, perfil=mi_perfil).exists():
            my_calification['valor'] = Calificacion.objects.get(libro=bk, perfil=mi_perfil)
        if Comentario.objects.filter(valor__libro=bk, perfil=mi_perfil).exists():
            my_calification['comentario'] = Comentario.objects.get(valor__libro=bk,perfil=mi_perfil)
            my_calification['id'] = int(my_calification['comentario'].id)
    comments = Comentario.objects.filter(valor__libro=bk).order_by('fecha_creacion')
    context = {'my_cal':my_calification, 'calform': calificacion, 'book': bk, 'chapters': chapters, 'comments': comments, 'hoy': date.today()}
    return render(request, 'libro.html', context)



def obtener_calificaciones(bk):
    if Calificacion.objects.filter(libro=bk).exists():
        book_califications = Calificacion.objects.filter(libro=bk)
        valor = int(sum(map(lambda x: x.valor, book_califications)) / len(book_califications))
    else:
        valor = 0
    stars = list(range(5))
    check = list(stars[:valor])
    uncheck = list(stars[valor:])
    calificacion = {'checked': check, 'unchecked': uncheck}
    return calificacion


def libro_terminado(bk, request):
    otro_perfil = Perfil.objects.filter(usuario=request.user).exclude(id=request.session['myProfile']).first()
    historial = LibroLeido.objects.filter(perfil=otro_perfil, libro=bk).first()
    try:
        if historial:
            return historial.terminado
        else:
            return True
    except:
        return True

def libro_capitulos_terminado(libro, request):
    otro_perfil = Perfil.objects.filter(usuario=request.user).exclude(id=request.session['myProfile']).first()
    historial = LibroLeido.objects.filter(Q(perfil=otro_perfil, cap__isnull=False))
    historial = historial.filter(Q(cap__libro=libro)).first()
    #try:
    if historial:
        return historial.terminado
    else:
        return True
    #except:
    #    return True


def listado_capitulos(request, libro_isbn):
    def chapters_for_basic(chapters):
        chaplist = list(filter(lambda x: x.fecha_lanzamiento_basico <= date.today(), chapters))
        return chaplist

    def chapters_for_premium(chapters):
        chaplist = list(filter(lambda x: (not x.fecha_lanzamiento_premium is None) and (x.fecha_lanzamiento_premium <= date.today()), chapters))
        chaplist = chaplist + chapters_for_basic(chapters)
        return list(filter(lambda x: x.fecha_vencimiento_premium is None or x.fecha_vencimiento_premium > date.today(), set(chaplist)))


    libro = Libro.objects.get(ISBN=libro_isbn)
    capis = Capitulo.objects.filter(libro=libro)
    if not request.user.is_staff:
        if request.user.subscription.nombre == 'Premium':
            capis =  chapters_for_premium(capis)
        else:
            if not libro_capitulos_terminado(libro, request):# en esa función se verifica que el libro no esté abierto en otro perfil de la cuenta
                messages.success(request, 'El libro que seleccionó está siendo leído por otro perfil de su cuenta.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context = {'capitulos': capis, 'libro': libro}
    return render(request, 'listado_capitulos.html', context)



def capitulo(request, capitulo_id):
    perfil = Perfil.objects.get(id=request.session['myProfile'])
    chap = Capitulo.objects.get(id=capitulo_id)
    if not request.user.is_staff:
        if request.user.subscription.nombre == 'Básico':
            if chap.exclusividad.nombre == 'Premium':
                messages.success(request, 'El capítulo que seleccionó es exclusivo para usuarios premium.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            if (chap.fecha_vencimiento_basico):
                if chap.fecha_vencimiento_basico <= date.today():
                    messages.success(request, 'El capítulo que seleccionó está vencido para su tipo de suscripción.')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if not LibroLeido.objects.filter(cap=chap, perfil=perfil).exists():  # se fija si existe en el historial
            nuevoLibroLeido = LibroLeido(perfil=perfil, cap=chap, terminado=False)    # como no esta en el historial crea un nuevo LibroLeido
            nuevoLibroLeido.save()
        else:
            historial = LibroLeido.objects.filter(cap=chap, perfil=perfil).first()
            historial.terminado = False
            historial.fecha = datetime.today()
            historial.save()  # como ya estaba este cap en el historial solamente le modifica la fecha de ultima visualizacion
    cont = get_pdf(chap.texto)
    try:
        siguiente = Capitulo.objects.filter(libro=chap.libro).get(indice=(chap.indice + 1))
    except:
        siguiente = 0
    try:
        anterior = Capitulo.objects.filter(libro=chap.libro).get(indice=(chap.indice - 1))
    except:
        anterior = 0

    context = {'capitulo': chap, 'ant': anterior, 'sig': siguiente, 'texto': cont}
    return render(request, 'capitulo.html', context)




def documento(request, libro_isbn):

    bk = Libro.objects.get(ISBN=libro_isbn)
    cont = get_pdf(bk.documento)
    if not request.user.is_staff:
        perfil = Perfil.objects.get(id=request.session['myProfile'])
        if request.user.subscription.nombre == 'Básico':
            if bk.exclusividad.nombre == 'Premium':

                messages.success(request, 'El libro que seleccionó es exclusivo para usuarios premium.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            elif not libro_terminado(bk, request): # en esa función se verifica que el libro no esté abierto en otro perfil de la cuenta
                messages.success(request, 'El libro que seleccionó está siendo leído por otro perfil de su cuenta.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            elif (bk.fecha_vencimiento_basico):
                if bk.fecha_vencimiento_basico <= date.today():
                    messages.success(request, 'El libro que seleccionó está vencido para su tipo de suscripción.')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if not LibroLeido.objects.filter(libro=bk, perfil=perfil).exists():  # se fija si existe en el historial
            nuevoLibroLeido = LibroLeido(perfil=perfil, libro=bk, terminado=False)
            nuevoLibroLeido.save()   # como no esta en el historial crea un nuevo LibroLeido
        else:
            historial = LibroLeido.objects.filter(libro=bk, perfil=perfil).first()
            historial.terminado = False
            historial.fecha = datetime.today()
            historial.save()  #  como ya estaba este libro en el historial solamente le modifica la fecha de ultima visualizacion

    context = {'cont': cont, 'libro':bk}
    return render(request, 'vistalibro.html', context)


def autores(request):
    authrs = Autor.objects.order_by('nombre')
    context = {'authors': authrs}
    return render(request, 'autores.html', context)


def generos(request):
    gnres = Genero.objects.order_by('nombre')
    context = {'genres': gnres}
    return render(request, 'generos.html', context)


def autor(request, autor_nombre):
    author = Autor.objects.get(nombre=autor_nombre)
    books = Libro.objects.filter(autor=author).order_by('titulo')
    context = {'author': author, 'books': books}
    return render(request, 'autor.html', context)


def genero(request, genero_nombre):
    gnre = Genero.objects.get(nombre=genero_nombre)
    books = Libro.objects.filter(genero=gnre).order_by('titulo')
    context = {'genre': gnre, 'books': books}
    return render(request, 'genero.html', context)


def editorial(request, editorial_nombre):
    edtr = Editorial.objects.get(nombre=editorial_nombre)
    books = Libro.objects.filter(editorial=edtr).order_by('titulo')
    context = {'edtr': edtr, 'books': books}
    return render(request, 'editorial.html', context)

def finalizar_lectura(request, libro_isbn):
    if not request.user.is_staff:
        book = Libro.objects.get(ISBN=libro_isbn)
        bk = LibroLeido.objects.filter(perfil=request.session['myProfile'], libro=book).first()
        bk.terminado = True
        bk.save()
        messages.info(request, 'Ha finalizado la lectura. Ahora puede calificar el libro.', extra_tags='algo')
    return redirect('libros:libro', libro_isbn)

def finalizar_capitulo(request, libro_isbn):
    if not request.user.is_staff:
        book = Libro.objects.get(ISBN=libro_isbn)
        capitulos = LibroLeido.objects.filter(Q(perfil=request.session['myProfile'], cap__isnull=False)).filter(Q(cap__libro=book))

        for cap in capitulos:
            cap.terminado = True
            cap.save()
        messages.info(request, 'Ha finalizado la lectura. Ahora puede calificar el libro.', extra_tags='algo')
    return redirect('libros:libro', libro_isbn)

@verificateUser
def historial(request):
    usuario = Perfil.objects.get(id=request.session['myProfile'])
    librosLeidos = LibroLeido.objects.filter(perfil=usuario).order_by('-ultima_fecha')
    context = {'usuario': usuario, 'librosLeidos': librosLeidos}  # dice 'libro' pero se refiere a libro y capitulo
    return render(request, 'historial.html', context)


@verificateUser
def busqueda(request):
    def buscar_por_autor(query):
        autores = Autor.objects.filter(nombre__icontains=query)
        result = []
        for autor in autores:
            result = result + list(Libro.objects.filter(autor=autor))
        return result

    def buscar_por_genero(query):
        generos = Genero.objects.filter(nombre__icontains=query)
        result = []
        for genero in generos:
            result = result + list(Libro.objects.filter(genero=genero))
        return result

    def buscar_por_editorial(query):
        editoriales = Editorial.objects.filter(nombre__icontains=query)
        result = []
        for editorial in editoriales:
            result = result + list(Libro.objects.filter(editorial=editorial))
        return result

    def buscar_por_titulo(query):
        result = Libro.objects.filter(titulo__icontains=query)
        return result
    search = request.GET.get('q')
    query= str(search).split(' ') #para que busque por palabra ingresada
    results = Libro.objects.all() #al principio se tiene todos los libros y con las búsquedas se empiezan a descartar

    for palabra in query:

        if buscar_por_autor(palabra): # si se encontró alguna coincidencia, se hace una intersección con los libros para descartar los que no coincidieron. Lo mismo con el resto de los criterios
            results = set(results) & set(buscar_por_autor(palabra))
        if buscar_por_genero(palabra):
            results = set(results) & set(buscar_por_genero(palabra))
        if buscar_por_titulo(palabra):
            results = set(results) & set(buscar_por_titulo(palabra))
        if buscar_por_editorial(palabra):
            results = set(results) & set(buscar_por_editorial(palabra))
    context = {}
    if len(results) == len(Libro.objects.all()): # si la cantidad de libros sigue siendo la misma del principio, es porque no se filtró nada y no hubo coincidencias, con lo cual, se devuelve una lista vacía
        results = []
        aviso = ''
        if request.method != 'POST':
            form = LibroSugeridoForm
        else:
            form = LibroSugeridoForm(data=request.POST)
            if form.is_valid():
                libro_sugerido_existente = LibroSugerido.objects.filter(sugerencia=form.cleaned_data['sugerencia']).first()
                perfil = Perfil.objects.get(id=request.session['myProfile'])
                if libro_sugerido_existente:
                    if perfil.librosugerido_set.filter(sugerencia=form.cleaned_data['sugerencia']).exists():
                        aviso = 'Ya sugeriste este libro anteriormente.'
                        pass
                    else:
                        libro_sugerido_existente.perfiles.add(perfil)
                        aviso = 'Gracias por su sugerencia'
                else:
                    nueva_sugerencia = form.save()
                    nueva_sugerencia.perfiles.add(perfil)
                    aviso = 'Gracias por su sugerencia,'
        context['form'] = form
        context['aviso'] = aviso
    elif not request.user.is_staff:
        if request.user.subscription.nombre == 'Premium':
            res = list(filter(lambda x: (not x.fecha_lanzamiento_premium is None) and (x.fecha_lanzamiento_premium <= date.today()), results))
            results = list(filter(lambda x: (x.fecha_vencimiento_premium is None) or x.fecha_vencimiento_premium > date.today(), set(res)))



    context['busqueda'] = search
    context['libros']= results
    return render(request, 'busqueda.html', context)

def calificar(request):
    book = Libro.objects.get(ISBN=request.POST['book'])
    prof = Perfil.objects.get(id=request.session['myProfile'])
    if Calificacion.objects.filter(libro=book, perfil=prof).exists():
        cal = Calificacion.objects.get(libro=book, perfil=prof)
    else:
        cal = Calificacion(libro=book, perfil=prof)
    cal.valor = (int(request.POST['value']) + 1)
    cal.save()
    comment = ''
    if request.POST['comment']:
        if Comentario.objects.filter(valor__libro=book, perfil=prof).exists():
            comentario = Comentario.objects.get(valor__libro=book, perfil=prof, libro=book)
        else:
            comentario = Comentario(perfil=prof, libro=book)
        comentario.valor = cal
        comentario.texto = request.POST['comment']
        if request.POST['spoiler'] == 'true':
            comentario.spoiler = True
        else:
            comentario.spoiler = False
        comentario.save()
        comment = comentario.texto
    mensaje = '<h5> Se ha guardado su calificación. </h5>'
    data = {'result': 'Success', 'message': mensaje, 'comment': comment}
    return HttpResponse(json.dumps(data), content_type='application/json')

def editar_comentario(request):
    book = Libro.objects.get(ISBN=int(request.POST['book']))
    prof = Perfil.objects.get(id=request.session['myProfile'])
    if Comentario.objects.filter(valor__libro=book, perfil=prof).exists():
        comentario = Comentario.objects.get(valor__libro=book, perfil=prof).texto
        data = {'result': 'Success', 'my_comment': comentario }
    else:
        data = {'result': 'Success', 'my_comment': '' }
    return HttpResponse(json.dumps(data), content_type='application/json')

def puedo_calificar(request):
    if not request.user.is_staff:
        book = Libro.objects.get(ISBN=int(request.POST['book']))
        prof = Perfil.objects.get(id=request.session['myProfile'])
        if LibroLeido.objects.filter(libro=book, perfil=prof).exists():
            if not LibroLeido.objects.get(libro=book, perfil=prof).terminado:
                data = {'result':'Error', 'message':'Debe finalizar la lectura de este libro para poder calificarlo.'}
            else:
                data = {'result': 'Success', 'my_comment': ''}
        else:
            data = {'result':'Error', 'message':'Usted no ha comenzado la lectura de este libro. Podrá calificarlo cuando finalice su lectura.'}
    else:
        data = {'result':'Error', 'message':'Usted no puede calificar el libro.'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def reportar_spoiler(request):
    prof = Perfil.objects.get(id=request.session['myProfile'])
    comment = Comentario.objects.get(id=int(request.POST['comment_id']))
    nuevo_reporte = ReporteSpoiler(comentario=comment, reportador=prof)
    nuevo_reporte.save()
    data = {'result': 'Success',
            'message': 'Se ha reportado el comentario. La situación será evaluada por los administradores de Bookflix.'}

    return HttpResponse(json.dumps(data), content_type='application/json')


def reportar_ofensivo(request):
    prof = Perfil.objects.get(id=request.session['myProfile'])
    comment = Comentario.objects.get(id=request.POST['comment'])
    nuevo_reporte = ReporteOfensivo(comentario=comment, reportador=prof)
    nuevo_reporte.save()
    data = {'result': 'Success',
            'message': 'Se ha reportado el comentario. La situación será evaluada por los administradores de Bookflix.'}

    return HttpResponse(json.dumps(data), content_type='application/json')


def eliminar_comentario(request):
    comentario = Comentario.objects.get(id=int(request.POST['book']))
    comentario.delete()
    mensaje = '<h5> Se ha eliminado su calificación. </h5>'
    data = {'result':'Success', 'message':mensaje }
    return HttpResponse(json.dumps(data), content_type='application/json')

def comentario_completo(request):
    comentario = Comentario.objects.get(id=int(request.POST['comment'])).texto
    data = {'result':'Success', 'comment':comentario }
    return HttpResponse(json.dumps(data), content_type='application/json')
