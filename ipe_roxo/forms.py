# forms.py

from django import forms
from .models import PlantaCuidador
from .models import Planta
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  


class ColaboradorForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nome de usuário',
            'email': 'E-mail'
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


class PlantaCuidadorForm(forms.ModelForm):
    class Meta:
        model = PlantaCuidador
        fields = ['nome', 'telefone', 'cidade', 'bairro', 'rua', 'numero', 'especie', 'idade',  'foto']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
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


class PlantaForm(forms.ModelForm):
    class Meta:
        model = Planta
        fields = ['especie', 'bairro']