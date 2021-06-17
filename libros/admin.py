from django.contrib.auth.admin import UserAdmin
from users.models import User, Membresia
from django.contrib import admin
from .models import Autor, Genero, Libro, Editorial, Capitulo, LibroLeido, Calificacion, Comentario, ReporteSpoiler, ReporteOfensivo, LibroSugerido
from django import forms
from datetime import date
from novedades.models import Novedad
from perfiles.models import Perfil

class MyUserAdmin(UserAdmin):
    model = User
    ordering = ['suspendida']
    list_filter = ('subscription', )
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('credit_Card', 'expired_Card', 'suspendida', 'subscription')}),
    )

class LibroForm(forms.ModelForm):
    cantidad_partes = forms.IntegerField(label="Cantidad de partes", initial=1, help_text='La cantidad máxima de capítulos o partes que componen al libro. Tenga en cuenta que si agrega un documento ahora, los posibles capítulos relacionados a este libro se perderán.')

    class Meta:
        model = Libro
        fields = '__all__'


    def clean(self):
        cleaned_data = super(LibroForm, self).clean()
        if 'documento' in cleaned_data.keys():
            if cleaned_data['documento']:
                try:
                    capitulos = Capitulo.objects.filter(libro=Libro.objects.get(ISBN=cleaned_data['ISBN']).id)
                    if capitulos:
                        capitulos.delete()
                except:
                    pass
                cleaned_data['cantidad_partes'] = 1

        if cleaned_data['fecha_lanzamiento_premium'] and cleaned_data['fecha_vencimiento_premium'] :
            begin_date = cleaned_data['fecha_lanzamiento_premium']
            expiration_date = cleaned_data['fecha_vencimiento_premium']
            if begin_date < date.today():
                raise forms.ValidationError("La fecha de lanzamiento para usuarios premium ingresada es incorrecta. La misma no puede ser menor que la actual.")
            if (expiration_date):
                if expiration_date < date.today():
                    raise forms.ValidationError("La fecha de vencimiento para usuarios premium ingresada es incorrecta. La fecha de vencimiento no puede ser menor que la actual.")

        elif 'exclusividad' in cleaned_data.keys():

            if (cleaned_data['exclusividad'].nombre == 'Premium' and not cleaned_data['fecha_lanzamiento_premium']):
                    raise forms.ValidationError("Por favor, ingrese una fecha de lanzamiento para suscripción premium.")


        if cleaned_data['fecha_lanzamiento_basico'] and cleaned_data['fecha_vencimiento_basico'] :
            begin_date = cleaned_data['fecha_lanzamiento_basico']
            expiration_date = cleaned_data['fecha_vencimiento_basico']
            if begin_date < date.today():
                raise forms.ValidationError("La fecha de lanzamiento ingresada es incorrecta. La fecha de lanzamiento no puede ser menor que la actual.")
            if (expiration_date):
                if expiration_date < date.today():
                    raise forms.ValidationError("La fecha de vencimiento ingresada es incorrecta. La fecha de vencimiento no puede ser menor que la actual.")
        elif 'exclusividad' in cleaned_data.keys():

            if cleaned_data['exclusividad'].nombre != 'Premium' and not cleaned_data['fecha_lanzamiento_basico']:
                    raise forms.ValidationError("Por favor, ingrese una fecha de lanzamiento para suscripción básica.")


        return self.cleaned_data



class LibroAdmin(admin.ModelAdmin):
    search_fields = ['ISBN','titulo', 'genero__nombre', 'editorial__nombre', 'autor__nombre']
    list_filter = ['autor', 'editorial', 'genero']
    form = LibroForm

class CapituloForm(forms.ModelForm):
    class Meta:
        model = Capitulo
        fields = '__all__'

    def clean(self):
        cleaned_data = super(CapituloForm, self).clean()
        if 'libro' in cleaned_data.keys():
            libr = Libro.objects.get(id=cleaned_data['libro'].id)
            if int(libr.cantidad_partes) < int(cleaned_data['indice']):
                raise forms.ValidationError('El índice ingresado es inválido.')

        if 'fecha_lanzamiento_premium' in cleaned_data.keys():
            if cleaned_data['fecha_lanzamiento_premium'] and cleaned_data['fecha_vencimiento_premium'] :
                begin_date = cleaned_data['fecha_lanzamiento_premium']
                expiration_date = cleaned_data['fecha_vencimiento_premium']
                if begin_date < date.today():
                    raise forms.ValidationError("La fecha de lanzamiento para usuarios premium ingresada es incorrecta. La misma no puede ser menor que la actual.")
                if (expiration_date):
                    if expiration_date < date.today():
                        raise forms.ValidationError("La fecha de vencimiento para usuarios premium ingresada es incorrecta. La fecha de vencimiento no puede ser menor que la actual.")
        else:
            raise forms.ValidationError('Ingrese una fecha de lanzamiento para premium')

        if 'exclusividad' in cleaned_data.keys():

            if (cleaned_data['exclusividad'].nombre == 'Premium' and not cleaned_data['fecha_lanzamiento_premium']):
                    raise forms.ValidationError("Por favor, ingrese una fecha de lanzamiento para suscripción premium.")


        if cleaned_data['fecha_lanzamiento_basico'] and cleaned_data['fecha_vencimiento_basico'] :
            begin_date = cleaned_data['fecha_lanzamiento_basico']
            expiration_date = cleaned_data['fecha_vencimiento_basico']
            if begin_date < date.today():
                raise forms.ValidationError("La fecha de lanzamiento ingresada es incorrecta. La fecha de lanzamiento no puede ser menor que la actual.")
            if (expiration_date):
                if expiration_date < date.today():
                    raise forms.ValidationError("La fecha de vencimiento ingresada es incorrecta. La fecha de vencimiento no puede ser menor que la actual.")
        elif 'exclusividad' in cleaned_data.keys():

            if cleaned_data['exclusividad'].nombre != 'Premium' and not cleaned_data['fecha_lanzamiento_basico']:
                    raise forms.ValidationError("Por favor, ingrese una fecha de lanzamiento para suscripción básica.")


        return self.cleaned_data

class CapituloAdmin(admin.ModelAdmin):
    search_fields = ['titulo', 'libro__titulo', 'libro__autor__nombre', 'libro__editorial__nombre']
    list_display = ['titulo', 'libro' ]
    list_filter = ['libro']
    ordering = ('libro',)
    form = CapituloForm

class NovedadForm(forms.ModelForm):
    class Meta:
        model = Novedad
        fields = '__all__'

    def clean(self):
        cleaned_data = super(NovedadForm, self).clean()

        if 'fechaLanzamiento' in cleaned_data.keys():
            begin_date = cleaned_data['fechaLanzamiento']
            if begin_date < date.today():
                raise forms.ValidationError("La fecha de lanzamiento ingresada es incorrecta.")

        if 'fechaExpiracion' in cleaned_data.keys():
            end_date = cleaned_data['fechaExpiracion']
            if end_date < begin_date:
                raise forms.ValidationError("La fecha de expiración no puede ser menor a la fecha de lanzamiento.")

        return self.cleaned_data


class NovedadAdmin(admin.ModelAdmin):
    form = NovedadForm

class GeneroForm(forms.ModelForm):
    class Meta:
        model = Genero
        fields = '__all__'

class GeneroAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    form = GeneroForm

class EditorialForm(forms.ModelForm):
    class Meta:
        model = Editorial
        fields = '__all__'

class EditorialAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    form = EditorialForm

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = '__all__'


class AutorAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    form = AutorForm

class ReporteSpoilerForm(forms.ModelForm):

    class Meta:
        model = ReporteSpoiler
        fields = '__all__'

class ReporteSpoilerAdmin(admin.ModelAdmin):

    fields = ('comentario','reportador')
    list_display = ['comentario', 'get_book']

    def get_book(self, obj):
        return obj.comentario.libro

    get_book.short_description = 'Libro comentado'

    form = ReporteSpoilerForm

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = '__all__'

class CalificacionAdmin(admin.ModelAdmin):
    search_fields = ['libro__titulo']
    list_display = ['valor', 'libro' ]
    list_filter = ['libro']
    ordering = ('libro',)
    form = CalificacionForm


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = '__all__'

class ComentarioAdmin(admin.ModelAdmin):
    search_fields = ['libro__titulo']
    list_display = ['texto', 'libro' ]
    list_filter = ['libro']
    ordering = ('libro',)
    form = ComentarioForm

class ReporteOfensivoForm(forms.ModelForm):

    class Meta:
        model = ReporteOfensivo
        fields = '__all__'

class ReporteOfensivoAdmin(admin.ModelAdmin):

    fields = ('comentario','reportador')
    list_display = ['comentario', 'get_book']

    def get_book(self, obj):
        return obj.comentario.libro

    get_book.short_description = 'Libro comentado'
    form = ReporteOfensivoForm

admin.site.register(Capitulo, CapituloAdmin)
admin.site.register(Perfil)
admin.site.register(LibroLeido)
admin.site.register(Calificacion, CalificacionAdmin)
admin.site.register(Comentario, ComentarioAdmin)
admin.site.register(Membresia)
admin.site.register(Novedad, NovedadAdmin)
admin.site.register(Autor, AutorAdmin)
admin.site.register(Genero, GeneroAdmin)
admin.site.register(Libro, LibroAdmin)
admin.site.register(Editorial, EditorialAdmin)
admin.site.register(User, MyUserAdmin)
admin.site.register(ReporteSpoiler, ReporteSpoilerAdmin)
admin.site.register(ReporteOfensivo, ReporteOfensivoAdmin)
admin.site.register(LibroSugerido)