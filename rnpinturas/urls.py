# rnpinturas/urls.py

"""
URL configuration for rnpinturas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from two_factor.urls import urlpatterns as tf_urls

from .views import home

urlpatterns = [
    #URL do Admin do Django
    path('admin/', admin.site.urls),

    # URL para a Página Inicial do Projeto
    path("", home, name="home"),

    # URL de Rotas de Autenticação (2FA)
    path('', include(tf_urls)),

    # URL de Rotas de Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # URLs dos Apps do Projeto
    path("", include("cities.urls")),
    path("", include("clients.urls")),
    path("common/", include("common.urls")),
]
