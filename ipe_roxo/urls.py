from django.urls import path
from . import views
from django.contrib.auth import views as auth_views




urlpatterns = [
    path('', views.home, name='home'),
    path('login/admin/', views.login_admin, name='login_admin'),
    path('login/colaborador/', views.login_colaborador, name='login_colaborador'),
    path('logout/', views.logout_view, name='logout'),
    path('colaborador/home_colaborador', views.home_colaborador, name='home_colaborador'),
    path('cadastro_plantas/', views.cadastrar_planta_cuidador, name='cadastrar_planta'),
    path('planta/<int:pk>/editar/', views.editar_planta, name='editar_planta'),
    path('formularios/', views.formularios_enviados, name='formularios_enviados'),


    path("formularios/<int:pk>/detalhe/", views.detalhes_formulario, name="detalhe_formulario"),

    path('home_admin/formularios-recebidos/', views.formularios_recebidos, name='formularios-recebidos'),
    path('home_admin/formulario/aprovar/<int:pk>/', views.FormularioAprovarView.as_view(), name='formulario-aprovar'),
    path('home_admin/formulario/corrigir/<int:pk>/', views.FormularioCorrigirView.as_view(), name='formulario-corrigir'),




    path('home_admin/', views.home_admin, name='home_admin'),
    path('ajuda/', views.ajuda, name='ajuda'),
    path('colaboradores/cadastrar/', views.cadastrar_colaborador, name='cadastrar_colaborador'),
    path('colaboradores/alternar-status/<int:colaborador_id>/', views.alternar_status_colaborador, name='alternar_status_colaborador'),
    path('colaboradores/editar/<int:colaborador_id>/', views.editar_colaborador, name='editar_colaborador'),
    path('colaboradores/excluir/<int:colaborador_id>/', views.excluir_colaborador, name='excluir_colaborador'),
    path('login/', auth_views.LoginView.as_view(template_name='ipe_roxo/login.html'), name='login'),
    path('home_admin/colaboradores/', views.listar_colaboradores, name='colaboradores'),


]