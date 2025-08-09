from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from .models import CustomUser
from .forms import ColaboradorForm

from .forms import PlantaCuidadorForm
from .models import PlantaCuidador
from django.db.models import Count, Q
from datetime import date
from django.views.decorators.http import require_POST

from django.contrib.auth import authenticate, login



def home(request):
    return render(request, 'ipe_roxo/index/home.html')

def login_admin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            user = CustomUser.objects.get(email=email, tipo='ADMIN')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Acesso restrito a administradores.')
            return redirect('login_admin')

        user = authenticate(request, username=user.username, password=senha)

        if user is not None:
            login(request, user)
            return redirect('home_admin')
        else:
            messages.error(request, 'Credenciais inválidas.')
            return redirect('login_admin')

    return render(request, 'ipe_roxo/admin/login_admin.html')


def login_colaborador(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            user = CustomUser.objects.get(email=email, tipo='COLAB', ativo=True)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Credenciais inválidas ou conta inativa.')
            return redirect('login_colaborador')

        user = authenticate(request, username=user.username, password=senha)

        if user is not None:
            login(request, user)
            return redirect('home_colaborador')
        else:
            messages.error(request, 'Credenciais inválidas.')
            return redirect('login_colaborador')

    return render(request, 'ipe_roxo/colaborador/login_colaborador.html')



def home_colaborador(request):

    return render(request, 'ipe_roxo/colaborador/home_colaborador.html')

def home_admin(request):

    return render(request, 'ipe_roxo/admin/home_admin.html')


def ajuda(request):
    return render(request, 'ipe_roxo/admin/ajuda.html')



def formularios_recebidos(request):
    return render(request, 'ipe_roxo/admin/formularios_recebidos.html')


def cadastrar_colaborador(request):
    if not request.user.is_authenticated or request.user.tipo != 'ADMIN':
        return redirect('login_admin')
    
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.tipo = 'COLAB'  # Garante que seja sempre colaborador
            user.save()
            messages.success(request, 'Colaborador cadastrado com sucesso!')
            return redirect('colaboradores')
    else:
        form = ColaboradorForm()
    
    return render(request, 'ipe_roxo/admin/cadastrar_colaborador.html', {'form': form})


@require_POST
def alternar_status_colaborador(request, colaborador_id):
    if not request.user.is_authenticated or request.user.tipo != 'ADMIN':
        return redirect('login_admin')
    
    colaborador = get_object_or_404(CustomUser, id=colaborador_id, tipo='COLAB')
    colaborador.ativo = not colaborador.ativo
    colaborador.save()
    
    status = "ativado" if colaborador.ativo else "desativado"
    messages.success(request, f'Colaborador {status} com sucesso!')
    return redirect('colaboradores')


def excluir_colaborador(request, colaborador_id):
    if not request.user.is_authenticated or request.user.tipo != 'ADMIN':
        return redirect('login_admin')
    
    colaborador = get_object_or_404(CustomUser, id=colaborador_id, tipo='COLAB')
    
    if request.method == 'POST':
        colaborador.delete()
        messages.success(request, 'Colaborador excluído com sucesso!')
    
    return redirect('colaboradores')

def editar_colaborador(request, colaborador_id):
    if not request.user.is_authenticated or request.user.tipo != 'ADMIN':
        return redirect('login_admin')
    
    colaborador = get_object_or_404(CustomUser, id=colaborador_id, tipo='COLAB')
    
    if request.method == 'POST':
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados do colaborador atualizados!')
            return redirect('colaboradores')
    else:
        form = ColaboradorForm(instance=colaborador)
    
    return render(request, 'ipe_roxo/admin/editar_colaborador.html', {
        'form': form,
        'colaborador': colaborador
    })

def listar_colaboradores(request):
    colaboradores = CustomUser.objects.all()

    # Pesquisar
    pesquisa = request.GET.get('pesquisa')
    if pesquisa:
        colaboradores = colaboradores.filter(
            Q(username__icontains=pesquisa) |
            Q(email__icontains=pesquisa)
        )

    # Filtro por status
    status = request.GET.get('status')
    if status == 'ativos':
        colaboradores = colaboradores.filter(is_active=True)
    elif status == 'inativos':
        colaboradores = colaboradores.filter(is_active=False)

    # Ordenação
    ordem = request.GET.get('ordem')
    if ordem == 'az':
        colaboradores = colaboradores.order_by('username')
    elif ordem == 'za':
        colaboradores = colaboradores.order_by('-username')

    context = {
        'colaboradores': colaboradores,
        'pesquisa': pesquisa,
        'status_filter': status,
        'ordem': ordem
    }
    return render(request, 'ipe_roxo/admin/colaboradores.html', context)

###########################################################################################################

@login_required
def formularios_enviados(request):
    formularios = PlantaCuidador.objects.filter(colaborador=request.user).order_by('-data_envio')
    return render(request, 'ipe_roxo/colaborador/formularios_enviados.html', {'formularios': formularios})



@login_required
def cadastrar_planta_cuidador(request):
    if request.method == 'POST':
        form = PlantaCuidadorForm(request.POST, request.FILES)
        if form.is_valid():
            planta = form.save(commit=False)
            planta.colaborador = request.user  # vincula o usuário logado
            planta.save()
            messages.success(request, 'Cadastro enviado com sucesso.')
            return redirect('formularios_enviados')
    else:
        form = PlantaCuidadorForm()
    return render(request, 'ipe_roxo/colaborador/cadastro_plantas.html', {'form': form})

@login_required
def editar_formulario(request, id):
    # Aqui pega o objeto PlantaCuidador, não o form!
    formulario = get_object_or_404(PlantaCuidador, id=id, colaborador=request.user)

    if formulario.status == 'aceito':
        messages.error(request, 'Formulário aceito não pode ser editado.')
        return redirect('formularios_enviados')

    if request.method == 'POST':
        form = PlantaCuidadorForm(request.POST, request.FILES, instance=formulario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Formulário atualizado com sucesso.')
            return redirect('formularios_enviados')
    else:
        form = PlantaCuidadorForm(instance=formulario)

    return render(request, 'ipe_roxo/colaborador/editar_formulario.html', {'form': form})

@login_required
def excluir_formulario(request, id):
    formulario = get_object_or_404(PlantaCuidador, id=id, colaborador=request.user)
    formulario.delete()
    messages.success(request, 'Formulário excluído com sucesso.')
    return redirect('formularios_enviados')

@login_required
def reenviar_formulario(request, id):
    formulario = get_object_or_404(PlantaCuidador, id=id, colaborador=request.user)

    if formulario.status != 'recusado':
        messages.error(request, 'Somente formulários recusados podem ser reenviados.')
        return redirect('formularios_enviados')

    formulario.status = 'pendente'
    formulario.observacao_admin = ''
    formulario.save()
    messages.success(request, 'Formulário reenviado para análise.')
    return redirect('formularios_enviados')