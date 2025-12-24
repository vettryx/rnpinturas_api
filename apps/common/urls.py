# apps/common/urls.py
from django.urls import path
from .views import api_busca_cep

app_name = 'common'

urlpatterns = [
    # Exemplo de URL: /common/api/cep/30000000/
    path('api/cep/<str:cep>/', api_busca_cep, name='api-busca-cep'),
]