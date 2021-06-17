
from django.urls import path, include
from . import views
from novedades.views import index


app_name = 'perfiles'
urlpatterns = [
    path('', index, name='index'),
    path('', include('django.contrib.auth.urls')),
    path('seleccionar/', views.seleccionarPerfil, name='seleccionarPerfil'),
    path('<int:perfil_id>/', views.viewIndex, name='iniciarPerfil'),
    path('eliminar/<int:perfil_id>', views.eliminarPerfil, name='eliminarPerfil'),
    path('nuevo/', views.nuevoPerfil, name='nuevoPerfil'),
    path('modificar/', views.modificarPerfil, name='modificarPerfil'),
    path('perfil/', views.verPerfil, name='verPerfil')
]