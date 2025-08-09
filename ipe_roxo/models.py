from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    TIPO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('COLAB', 'Colaborador'),
    ]
    tipo = models.CharField(max_length=5, choices=TIPO_CHOICES, default='COLAB')
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.username




class PlantaCuidador(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aceito', 'Aceito'),
        ('recusado', 'Recusado'),
    ]

    colaborador = models.ForeignKey( CustomUser, on_delete=models.CASCADE, related_name='formularios')
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    cidade = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    rua = models.CharField(max_length=100)
    numero = models.CharField(max_length=20)
    especie = models.CharField(max_length=100)
    idade = models.CharField(max_length=50)
    data = models.DateField()
    foto = models.ImageField(upload_to='fotos_plantas/')
    data_envio = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    observacao_admin = models.TextField(blank=True)

    def __str__(self):
        return f"{self.especie} - {self.colaborador.username}"
    



class Planta(models.Model):
    colaborador = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    especie = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    data_envio = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[('pendente', 'Pendente'), ('aceito', 'Aceito'), ('recusado', 'Recusado')],
        default='pendente'
    )
    observacao_admin = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.especie} - {self.bairro} ({self.status})'