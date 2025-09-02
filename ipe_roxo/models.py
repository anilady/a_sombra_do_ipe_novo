from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid



class CustomUser(AbstractUser):
    TIPO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('COLAB', 'Colaborador'),
    ]
    tipo = models.CharField(max_length=5, choices=TIPO_CHOICES, default='COLAB')
    ativo = models.BooleanField(default=True)
    funcao = models.CharField(max_length=100, blank=True, null=True)  # Novo campo função


    def __str__(self):
        return self.username


#########################################################################################

class PlantaCuidador(models.Model): 
    STATUS_CHOICES = [ ('PENDENTE', 'Pendente de revisão'), ('APROVADO', 'Aprovado'), ('CORRECAO', 'Necessita correções'), ] 
    STATUS_PLANTA_CHOICES = [('VIVA', 'Planta Viva'),('MORTA', 'Planta Morta'),('REPLANTADA', 'Replantada'),]
    status = models.CharField( max_length=10, choices=STATUS_CHOICES, default='PENDENTE' ) 
    status_planta = models.CharField(max_length=20,choices=STATUS_PLANTA_CHOICES,default='VIVA')
    admin_responsavel = models.ForeignKey( CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='formularios_revisados' ) 
    motivo_correcao = models.TextField(blank=True, null=True)
    numero_registro = models.CharField(max_length=12,unique=True,null=True,blank=True,editable=False) 
    horario_cadastro = models.DateTimeField(default=timezone.now) # Novo campo 
    colaborador = models.ForeignKey( CustomUser, on_delete=models.CASCADE, related_name='formularios') 
    nome = models.CharField(max_length=100) 
    ativo = models.BooleanField(default=True) 
    telefone = models.CharField(max_length=11) 
    cidade = models.CharField(max_length=100) 
    bairro = models.CharField(max_length=100)
    rua = models.CharField(max_length=100) 
    numero = models.CharField(max_length=20) 
    especie = models.CharField(max_length=100) 
    idade = models.CharField(max_length=50) 
    data = models.DateField() 
    foto = models.ImageField(upload_to='fotos_plantas/') 
    data_envio = models.DateTimeField(auto_now_add=True) 
    observacao_admin = models.TextField(blank=True) 
    def save(self, *args, **kwargs):
        if not self.pk and not self.numero_registro:  # Só para novos registros
            self.numero_registro = timezone.now().strftime("IP%Y%m") + str(uuid.uuid4().hex[:6]).upper()
        super().save(*args, **kwargs)  # Agora sempre salva

    def __str__(self):
        return f"{self.numero_registro} - {self.nome}"


#################################3##
class PlantaHistorico(models.Model):
    planta = models.ForeignKey("PlantaCuidador", on_delete=models.CASCADE, related_name="historicos")
    foto = models.ImageField(upload_to="plantas/historico/", blank=True, null=True)
    data_evento = models.DateTimeField(auto_now_add=True)
    descricao = models.TextField(blank=True, null=True)  # Ex: "Nova foto após 3 meses", "Planta morreu", etc.
    status_planta= models.CharField(
        max_length=20,
        choices=[
            ('VIVA', 'Planta Viva'),
            ('MORTA', 'Planta Morta'),
            ('REPLANTADA', 'Replantada'),
        ],
        default='VIVA'
    )

    def __str__(self):
        return f"Histórico da {self.planta.id} - {self.data_evento}"