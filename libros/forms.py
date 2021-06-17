from django import forms
from .models import LibroSugerido


class LibroSugeridoForm(forms.ModelForm):
    class Meta:
        model = LibroSugerido
        fields = ['sugerencia']
        labels = {'sugerencia': ''}