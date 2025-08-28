# forms.py

from django import forms
from .models import PlantaCuidador
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  
import re
from django.core.exceptions import ValidationError
from django.utils import timezone




class ColaboradorForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email','funcao', 'password1', 'password2']
        labels = {
            'username': 'Usuário',
            'email': 'E-mail',
            'funcao': 'Função'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove a ajuda do username (opcional)
        self.fields['username'].help_text = None
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email


class ColaboradorEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email','funcao']  # só esses campos, sem senha e sem função

        labels = {
            'username': 'Nome de usuário',
            'email': 'E-mail',
            'funcao': 'Função'
        }

##############################################################################################################

class PlantaCuidadorForm(forms.ModelForm):
    class Meta:
        model = PlantaCuidador
        fields = ['nome', 'telefone', 'cidade', 'bairro', 'rua', 'numero', 'especie', 'idade', 'data', 'foto']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'telefone': forms.TextInput(attrs={'placeholder': 'Com ddd '}),
            'numero': forms.NumberInput(attrs={'min': 1}),
        }
        labels = {
            'nome': 'Nome do Cuidador',
            'telefone': 'Telefone do Cuidador',
            'cidade': 'Cidade',
            'bairro': 'Bairro',
            'rua': 'Rua',
            'numero': 'Número',
            'especie': 'Espécie da Planta',
            'idade': 'Idade Aproximada',
            'data': 'Data do Plantio',
            'foto': 'Foto da Planta',
        }

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if not re.match(r'^\d{11}$', telefone):  # Verifica 9 dígitos
            raise ValidationError("O telefone deve conter exatamente 9 números + ddd")
        return telefone

    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if not str(numero).isdigit():
            raise ValidationError("O número deve conter apenas dígitos")
        return numero

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.horario_cadastro = timezone.now()  # Adiciona horário atual automaticamente
        if commit:
            instance.save()
        return instance



