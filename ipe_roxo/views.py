from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CustomUser
from .forms import ColaboradorForm
from .forms import ColaboradorEditForm
from django.utils import timezone

import json

from .forms import PlantaCuidadorForm
from django.http import JsonResponse
from .models import PlantaCuidador, PlantaHistorico


from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.db.models import Count
from django.db.models.functions import TruncMonth
import calendar


from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout

##############################################


def csrf_failure(request, reason=""):
    context = {
        'reason': reason,
    }
    return render(request, 'ipe_roxo/index/csrf_failure.html', context, status=403)


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

@login_required
def home_colaborador(request):
    # Filtrar plantas do usuário logado
    plantas = PlantaCuidador.objects.filter(colaborador=request.user)

    # Gráfico de Pizza
    grafico_pizza = {
        "vivas": plantas.filter(status_planta="VIVA").count(),
        "mortas": plantas.filter(status_planta="MORTA").count(),
        "replantadas": plantas.filter(status_planta="REPLANTADA").count(),
    }

    # Gráfico de Linha - Plantios por mês
    mensal = (
        plantas.annotate(mes=TruncMonth("data"))
        .values("mes")
        .annotate(total=Count("id"))
        .order_by("mes")
    )


    meses = []
    totais = []
    for item in mensal:
        nome_mes = calendar.month_name[item["mes"].month]
        meses.append(f"{nome_mes}/{item['mes'].year}")
        totais.append(item["total"])

    grafico_linha = {
        "meses": json.dumps(meses),   # Para uso direto em JS
        "totais": json.dumps(totais),
    }

    return render(
        request,
        "ipe_roxo/colaborador/home_colaborador.html",
        {
            "grafico_pizza": grafico_pizza,
            "grafico_linha": grafico_linha,
        }
    )


def home_admin(request):
    if not request.user.is_authenticated or request.user.tipo != 'ADMIN':
        return redirect('login_admin')
    
    # Buscar apenas formulários APROVADOS
    formularios_aprovados = PlantaCuidador.objects.filter(status='APROVADO')
    
    # Calcular totais
    total_arvores = PlantaCuidador.objects.all().count()
    total_vivas = PlantaCuidador.objects.filter(status_planta='VIVA').count()
    total_mortas = PlantaCuidador.objects.filter(status_planta='MORTA').count()
    total_replantadas = PlantaCuidador.objects.filter(status_planta='REPLANTADA').count()

    # Taxa de sobrevivência (vivas / total)
    taxa_sobrevivencia = (total_vivas / total_arvores * 100) if total_arvores > 0 else 0
    
    # Dados para gráfico mensal (manter lógica atual)
    dados_mensais = obter_dados_mensais_plantios()
    dados_mensais_json = json.dumps(dados_mensais, default=str)

    # Pesquisar
    pesquisa = request.GET.get('pesquisa')
    if pesquisa:
        formularios_aprovados = formularios_aprovados.filter(
            Q(numero_registro__icontains=pesquisa) |
            Q(nome__icontains=pesquisa) |
            Q(especie__icontains=pesquisa) |
            Q(bairro__icontains=pesquisa)
        )

    # Filtro por situação
    status_planta= request.GET.get('status_planta')
    if status_planta in ['VIVA', 'MORTA', 'REPLANTADA']:
        formularios_aprovados = formularios_aprovados.filter(status_planta=status_planta)

    # Ordenação
    ordem = request.GET.get('ordem')
    if ordem == 'mais_recente':
        formularios_aprovados = formularios_aprovados.order_by('-data_envio')
    elif ordem == 'menos_recente':
        formularios_aprovados = formularios_aprovados.order_by('data_envio')


    # Contexto
    context = {
        'formularios': formularios_aprovados,
        'total_arvores': total_arvores,
        'total_vivas': total_vivas,
        'total_mortas': total_mortas,
        'total_replantadas': total_replantadas,
        'taxa_sobrevivencia': taxa_sobrevivencia,
        'dados_mensais': dados_mensais_json,
        'pesquisa': pesquisa,
        'status_filter': status_planta,
        'ordem': ordem,
    }

    return render(request, 'ipe_roxo/admin/home_admin.html', context)

    

def obter_dados_mensais_plantios():
    # Plantios por mês (apenas aprovados)
    dados = (PlantaCuidador.objects
             .filter(status='APROVADO', data__isnull=False)
             .annotate(mes=TruncMonth('data'))
             .values('mes')
             .annotate(quantidade=Count('id'))
             .order_by('mes'))
    
    return list(dados)



def ajuda(request):
    return render(request, 'ipe_roxo/admin/ajuda.html')


def logout_view(request):
    # Realiza o logout
    logout(request)
    
    # Redireciona o usuário para a página de login ou qualquer página desejada
    return redirect('login')



def cadastrar_colaborador(request):
    if not request.user.is_authenticated or request.user.tipo != 'ADMIN':
        return redirect('login_admin')
    
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.tipo = 'COLAB'  # Garante que seja sempre colaborador
            user.is_staff = False

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
        form = ColaboradorEditForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados do colaborador atualizados!')
            return redirect('colaboradores')
    else:
        form = ColaboradorEditForm(instance=colaborador)
    
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
        colaboradores = colaboradores.filter(ativo=True)
    elif status == 'inativos':
        colaboradores = colaboradores.filter(ativo=False)

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
def cadastrar_planta_cuidador(request):
    if request.method == 'POST':
        form = PlantaCuidadorForm(request.POST, request.FILES)
        if form.is_valid():
            planta = form.save(commit=False)
            planta.colaborador = request.user  # Vincula o usuário logado
            planta.horario_cadastro = timezone.now()  # Adiciona horário atual
            planta.save()


            messages.success(request, 'Cadastro enviado com sucesso! Aguarde aprovação.')
            return redirect('formularios_enviados')

    else:
        form = PlantaCuidadorForm()
    
    return render(request, 'ipe_roxo/colaborador/cadastro_plantas.html', {
        'form': form,

        'hoje': timezone.now().strftime('%Y-%m-%d')  # Para limitar a data no HTML
    })

def editar_planta(request, pk):
    planta = get_object_or_404(PlantaCuidador, pk=pk)

    if request.method == 'POST':
        form = PlantaCuidadorForm(request.POST, request.FILES, instance=planta)
        if form.is_valid():
            planta = form.save(commit=False)
            
            # Mantém status do formulário como PENDENTE
            planta.status = "PENDENTE"
            
            # Atualiza status_planta apenas se enviado
            nova_condicao = request.POST.get('status_planta')
            if nova_condicao in ['VIVA', 'MORTA', 'REPLANTADA']:
                planta.status_planta = nova_condicao

            planta.save()

            PlantaHistorico.objects.create(
                planta=planta,
                foto=request.FILES.get('foto'),   # se enviou nova foto
                descricao=f"Formulário editado. Condição da planta: {planta.status_planta}"
            )

            messages.success(request, 'Planta atualizada com sucesso e enviada para nova avaliação!')
            return redirect('formularios_enviados')
    else:
        form = PlantaCuidadorForm(instance=planta)

    return render(request, 'ipe_roxo/colaborador/editar_form.html', {'form': form, 'planta': planta})



@login_required
def formularios_enviados(request):
    formularios = PlantaCuidador.objects.filter(colaborador=request.user).order_by('-data_envio')

    # Pesquisar
    pesquisa = request.GET.get('pesquisa')
    if pesquisa:
        formularios = formularios.filter(
            Q(numero_registro__icontains=pesquisa) |   # Pesquisa por Nº Registro
            Q(nome__icontains=pesquisa) |               # Pesquisa por Nome
            Q(especie__icontains=pesquisa) |            # Pesquisa por Espécie
            Q(bairro__icontains=pesquisa)               # Pesquisa por Bairro
        )

    # Filtro por status
    status = request.GET.get('status')
    if status in ['PENDENTE', 'APROVADO', 'CORRECAO']:
        formularios = formularios.filter(status=status)

    # Filtro por status_planta (VIVA, MORTA, REPLANTADA)
    status_planta = request.GET.get('status_planta')
    if status_planta in ['VIVA', 'MORTA', 'REPLANTADA']:
        formularios = formularios.filter(status_planta=status_planta)

    # Ordenação
    ordem = request.GET.get('ordem')
    if ordem == 'mais_recente':
        formularios = formularios.order_by('-data_envio')  # Mais recente
    elif ordem == 'menos_recente':
        formularios = formularios.order_by('data_envio')   # Menos recente

    ordem_choices = [
        ('mais_recente', 'Recentes'),
        ('menos_recente', 'Antigos')
    ]
    status_choices = PlantaCuidador.STATUS_CHOICES

    # Contexto
    context = {
        'formularios': formularios,
        'pesquisa': pesquisa,
        'status_filter': status,
        'status_planta_filter': status_planta,  # Adicionando o filtro de status_planta
        'ordem': ordem,
        'ordem_choices': ordem_choices, 
        'status_choices': status_choices,
    }

    return render(request, 'ipe_roxo/colaborador/formularios_enviados.html', context)


@login_required
def detalhes_formulario(request, pk):
    if request.user.tipo == 'ADMIN':
        # Admin pode ver qualquer planta
        planta = get_object_or_404(PlantaCuidador, pk=pk)
    else:
        # Colaborador só pode ver suas próprias plantas
        planta = get_object_or_404(PlantaCuidador, pk=pk, colaborador=request.user)

    # Em ambos os casos, traz o histórico da planta
    historicos = planta.historicos.all().order_by("-data_evento")

    return render(request,"ipe_roxo/colaborador/detalhe_formulario.html",{"planta": planta, "historicos": historicos})

###################################################################################################
def is_admin(user):
    return user.is_authenticated and user.tipo == 'ADMIN'

@login_required
@user_passes_test(is_admin)
def formularios_recebidos(request):
    # Mostra apenas formulários pendentes (aguardando análise do administrador)
    formularios = PlantaCuidador.objects.filter(
        status='PENDENTE'
    ).select_related('colaborador').order_by('-horario_cadastro')
    
    return render(request, 'ipe_roxo/admin/formularios_recebidos.html', {
        'formularios': formularios
    })

class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin para verificar se o usuário é admin"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.tipo == 'ADMIN'

class BaseFormularioView(LoginRequiredMixin, StaffRequiredMixin, View):
    """View base para ações de formulário"""
    model = PlantaCuidador
    
    def get_formulario(self):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


class FormularioAprovarView(BaseFormularioView):
    def post(self, request, *args, **kwargs):
        formulario = get_object_or_404(self.model, pk=self.kwargs['pk'])
        
        if formulario.status == 'APROVADO':
            return JsonResponse({
                'status': 'error',
                'message': 'Este formulário já foi aprovado.'
            })

        formulario.status = 'APROVADO'
        formulario.admin_responsavel = request.user
        formulario.motivo_correcao = None
        formulario.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Formulário aprovado com sucesso!'
        })

class FormularioCorrigirView(BaseFormularioView):
    """View para solicitar correção - SOME da lista"""
    
    def post(self, request, *args, **kwargs):
        formulario = self.get_formulario()
        
        try:
            motivo = request.POST.get('motivo', '').strip()
            
            if not motivo:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Motivo da correção é obrigatório.'
                })
            
            if len(motivo) < 10:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'O motivo deve ter pelo menos 10 caracteres.'
                })
            
            # SOLICITA CORREÇÃO - status muda para CORRECAO
            formulario.status = 'CORRECAO'
            formulario.motivo_correcao = motivo
            formulario.admin_responsavel = request.user
            formulario.save()

            
            return JsonResponse({
                'status': 'success', 
                'message': 'Correção solicitada com sucesso! O formulário será revisado novamente após as correções.'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Erro ao solicitar correção: {str(e)}'
            })
        
#########################################################
