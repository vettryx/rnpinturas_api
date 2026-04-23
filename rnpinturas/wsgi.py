"""
==============================================================================
Módulo: Configuração WSGI (Produção)
Caminho: rnpinturas/wsgi.py
==============================================================================

Configuração da interface WSGI para o servidor de aplicação. Define o ponto
de entrada para o Django e estabelece a ponte de comunicação necessária
para o ambiente Serverless da Vercel através da variável 'app'.
==============================================================================
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rnpinturas.settings")

application = get_wsgi_application()

# Ponte de comunicação para o runtime da Vercel
app = application
