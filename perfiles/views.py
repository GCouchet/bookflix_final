from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import crearPerfil
from .models import Perfil
from novedades.views import extendsContext
from libros.views import verificateUser
from libros.models import LibroLeido

def nuevoPerfil(request):
    usuario = request.user
    perfiles = Perfil.objects.filter(usuario=usuario)
    countProfiles = perfiles.count()
    def existePerfil(nom):

        return perfiles.filter(nombre=nom)

    if (countProfiles == usuario.subscription.limitePerfiles):
        context= extendsContext(request, {'usuario':usuario})
        return render(request, 'error.html', context)
    else:
        if request.method != 'POST':
            # se muestra un form en blanco para registrarlo
            form = crearPerfil()
        else:
            # se procesa un form completado

            form = crearPerfil(request.POST)
            formulario = request.POST.copy()
            if form.is_valid():
                if not existePerfil(formulario.get('nombre')):

                    if (not usuario.subscription is None):
                        new_profile = form.save(commit=False)
                        new_profile.usuario = usuario
                        new_profile.save()
                        messages.success(request, 'Perfil creado correctamente.')
                        return seleccionarPerfil(request)
                else:
                    messages.success(request, 'Ya existe un perfil con ese nombre. Por favor, ingrese uno diferente.')

    context = extendsContext(request, {'form': form})

    return render(request, 'nuevoPerfil.html', context)

def seleccionarPerfil(request):
    if (request.user.suspendida == None) or (not request.user.is_suspended):
        request.session['myProfile'] = None
        if request.user.is_staff:
            profiles = Perfil.objects.get(usuario=request.user)
            return viewIndex(request, profiles.id)
        else:
            profiles = Perfil.objects.all()
            profiles = profiles.filter(usuario=request.user)
            context = {'perfiles': profiles}
            return render(request, 'seleccionarPerfil.html', context)
    else:
        messages.success(request, 'Su cuenta se encuentra suspendida por falta de pago. Por favor, regularice su situación.')
        return redirect('users:logout')

def eliminarPerfil(request, perfil_id):
    Perfil.objects.get(id=perfil_id).delete()
    messages.success(request, 'Su perfil se eliminó correctamente.')
    return seleccionarPerfil(request)

def modificarPerfil(request):
    usuario = request.user
    perfiles = Perfil.objects.filter(usuario=usuario)

    def existePerfil(nom):
        return perfiles.filter(nombre=nom)

    p = Perfil.objects.get(id=request.session['myProfile'])
    form = crearPerfil(instance=p)
    if request.method != 'POST':
        form = crearPerfil(instance=p)
    else:
        form = crearPerfil(request.POST, instance=p)
        formulario = request.POST.copy()
        if form.is_valid():
            if not existePerfil(formulario.get('nombre')):
                form.save()
                messages.success(request, 'Su nombre se ha modificado exitosamente.')
                return redirect('perfiles:verPerfil')
            else:
                messages.success(request, 'Ya existe un perfil con ese nombre. Por favor, ingrese uno diferente.')
                return redirect('perfiles:verPerfil')

    context = extendsContext(request, {'form': form})
    return render(request, 'modificarPerfil.html', context)

def viewIndex(request, perfil_id):
    #profile = Perfil.objects.get(id=perfil_id)
    request.session['myProfile'] = perfil_id
    #request.session.set_expiry(0) ¿como borro el atributo (del request.session['myProfile'])
    #novs = Novedad.objects.order_by('fechaLanzamiento').reverse()[0:3]
    #novss = filter(lambda x : x.fechaLanzamiento <= date.today()  and x.fechaExpiracion > date.today(), novs )
    #bookslsts = Libro.objects.order_by('fecha_creacion').reverse()[0:6]
    #bookslst = filter(lambda x : x.fecha_lanzamiento <= date.today(), bookslsts )
    return redirect('novedades:index')

@verificateUser
def verPerfil(request):
    #try:
        profile = Perfil.objects.get(id=request.session['myProfile'])
        librosLeidos = list(LibroLeido.objects.filter(perfil=profile).order_by('-ultima_fecha'))[0:4]
        context = extendsContext(request, {'perfil': profile, 'librosLeidos':librosLeidos})
        return render(request, 'verPerfil.html', context)
   # except:
        #return seleccionarPerfil(request)

