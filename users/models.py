from django.contrib.auth.models import AbstractUser
from django.db import models
from creditcards.models import CardNumberField, CardExpiryField, SecurityCodeField
from datetime import date


class Membresia(models.Model):
    nombre = models.CharField(max_length=10)
    limitePerfiles = models.PositiveSmallIntegerField()
    limiteSesionesActivas = models.PositiveSmallIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

class User(AbstractUser):
    credit_Card = CardNumberField('Número de tarjeta', null=True, unique=True)
    expired_Card = CardExpiryField('Vencimiento',  null=True)
    secCode_Card = SecurityCodeField('Código de seguridad', null=True)
    tipo_tarjeta = models.CharField('Tipo de tarjeta', null=True, max_length=60)
    titular = models.CharField('Nombre del titular de la tarjeta', null=True, max_length=60)
    subscription = models.ForeignKey(Membresia, on_delete=models.CASCADE, null=True)
    dni = models.IntegerField('DNI del titular de la tarjeta', null=True)
    suspendida = models.DateField('Vencimiento de la membresía', null=True, blank=True)

    def __str__(self):
        return self.username

    @property
    def is_suspended(self):
        return date.today() > self.suspendida

    class Meta:
        ordering = ['suspendida']