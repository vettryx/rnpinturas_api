"""
==============================================================================
Módulo: Roteamento Principal (Projeto)
Caminho: rnpinturas/urls.py
==============================================================================

Configuração de URLs global do projeto RN Pinturas.
Gerencia as rotas de administração, autenticação (2FA), contas e a
integração modular dos aplicativos do sistema.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from two_factor.urls import urlpatterns as tf_urls

from .views import home

urlpatterns = [
    # ==========================================================================
    # CORE E ADMINISTRAÇÃO
    # ==========================================================================

    # URL do Admin do Django
    path("admin/", admin.site.urls),

    # URL para a Página Inicial do Projeto
    path("", home, name="home"),

    # ==========================================================================
    # AUTENTICAÇÃO E CONTAS
    # ==========================================================================

    # URL de Rotas de Autenticação (2FA)
    path("", include(tf_urls)),

    # URLs de Troca de Senha
    path("account/password/", auth_views.PasswordChangeView.as_view(), name="password_change"),
    path(
        "account/password/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),

    # URL de Rotas de Logout
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # ==========================================================================
    # MÓDULOS DO PROJETO (APPS)
    # ==========================================================================

    path("", include("cities.urls")),
    path("", include("clients.urls")),
    path("", include("materials.urls")),
    path("", include("orders.urls")),
    path("", include("rooms.urls")),
    path("", include("services.urls")),
    path("common/", include("common.urls")),
]
