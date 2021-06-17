from django.urls import path
from libros import views

app_name = 'libros'
urlpatterns = [
    path('index', views.index, name='index'),
    path('listado_libros/', views.libros, name='listado_libros'),
    path('listado_libros/<int:libro_isbn>/', views.libro, name='libro'),
    path('listado_capitulos/<int:libro_isbn>/', views.listado_capitulos, name='listado_capitulos'),
    path('capitulo/<int:capitulo_id>', views.capitulo, name='capitulo'),
    path('libro_view/<int:libro_isbn>', views.documento, name='vistalibro'),
    path('autores/', views.autores, name='autores'),
    path('autor/<str:autor_nombre>/', views.autor, name='autor'),
    path('genres/', views.generos, name='genres'),
    path('genero/<str:genero_nombre>/', views.genero, name='genero'),
    path('editorial/<str:editorial_nombre>/', views.editorial, name='editorial'),
    path('historial/', views.historial, name='historial'),
    path('busqueda/', views.busqueda, name='busqueda'),
    path('finalizar/<int:libro_isbn>', views.finalizar_lectura, name='finalizar'),
    path('finalizarcapitulo/<int:libro_isbn>', views.finalizar_capitulo, name='finalizarcapitulo'),
    path('editar_comentario/', views.editar_comentario, name='editar_comentario'),
    path('calificar/', views.calificar, name='calificar'),
    path('calificacion/', views.puedo_calificar, name='calificacion'),
    path('eliminar_comentario/', views.eliminar_comentario, name='eliminar_comentario'),
    path('ccomentario/', views.comentario_completo, name='comentario_completo'),
    path('reportar_spoiler/', views.reportar_spoiler, name='reportar_spoiler'),
    path('reportar_ofensivo/', views.reportar_ofensivo, name='reportar_ofensivo'),


]
