from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Membresia
from creditcards.models import CardNumberField, CardExpiryField, SecurityCodeField

# Extendemos del original
class UCFWithExtends(UserCreationForm):
    # Ahora el campo username es de tipo email y cambiamos su texto
    username = forms.EmailField(max_length=50, widget=forms.TextInput(attrs={'size':'50px'}), label='Dirección de correo electrónico')
    first_name = forms.CharField(max_length=30, label="Nombre", widget=forms.TextInput(attrs={'size':'50px'}))
    last_name = forms.CharField(max_length=30, label="Apellido", widget=forms.TextInput(attrs={'size':'50px'}))
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'size':'50px'}))
    password2 = forms.CharField(label="Confirmación de contraseña", widget=forms.PasswordInput(attrs={'size':'50px'}))
    subscription = forms.ModelChoiceField(queryset=Membresia.objects.all(), label="Subscripción")
    titular = forms.CharField(label='Nombre del titular de la tarjeta', max_length=60, widget=forms.TextInput(attrs={'size':'50px'}))
    dni = forms.CharField(label="DNI del titular de la tarjeta", widget=forms.TextInput(attrs={'size':'50px'}))
    tipo_tarjeta = forms.ChoiceField(choices=[('Crédito', 'Crédito')]+[('Débito', 'Débito')], label='Tipo de tarjeta')
    credit_Card = forms.CharField(widget=forms.TextInput(attrs={'size':'50px'}), label="Número de la tarjeta")
    expired_Card = CardExpiryField('Vencimiento')
    secCode_Card = forms.CharField(label="Código de seguridad de la tarjeta", widget=forms.PasswordInput(attrs={'size':'50px'}))

    class Meta:
        model = User
        fields = [ "username", "first_name", "last_name", "password1", "password2", "credit_Card", "expired_Card", "secCode_Card", "subscription", "dni", "titular", "tipo_tarjeta"]



class configurarCuenta(forms.ModelForm):

    username = forms.EmailField(max_length=50, widget=forms.TextInput(attrs={'size':'50px'}), label='Dirección de correo electrónico')
    first_name = forms.CharField(max_length=30, label="Nombre", widget=forms.TextInput(attrs={'size':'50px'}))
    last_name = forms.CharField(max_length=30, label="Apellido", widget=forms.TextInput(attrs={'size':'50px'}))
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'size':'50px'}))
    password2 = forms.CharField(label="Confirmación de contraseña", widget=forms.PasswordInput(attrs={'size':'50px'}))
    subscription = forms.ModelChoiceField(queryset=Membresia.objects.all(), label="Subscripción")
    titular = forms.CharField(label='Nombre del titular de la tarjeta', max_length=60, widget=forms.TextInput(attrs={'size':'50px'}))
    dni = forms.CharField(label="DNI del titular de la tarjeta", widget=forms.TextInput(attrs={'size':'50px'}))
    tipo_tarjeta = forms.ChoiceField(choices=[('Crédito', 'Crédito')]+[('Débito', 'Débito')], label='Tipo de tarjeta')
    credit_Card = forms.CharField(widget=forms.TextInput(attrs={'size':'50px'}), label="Número de la tarjeta")
    expired_Card = CardExpiryField('Vencimiento')
    secCode_Card = forms.CharField(label="Código de seguridad de la tarjeta", widget=forms.PasswordInput(attrs={'size':'50px'}))

    class Meta:
        model = User
        fields = [ "username", "first_name", "last_name", "password1", "password2", "credit_Card", "expired_Card", "secCode_Card", "subscription", "dni", "titular", "tipo_tarjeta"]
