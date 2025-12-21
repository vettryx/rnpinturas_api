# rnpinturas/settings.py

"""
Configurações do Django para o projeto RN Pinturas.
Baseado na estrutura moderna com Pathlib e boas práticas de produção.
"""

from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# --- CONFIGURAÇÃO DE CAMINHOS ---
# Definição do diretório base do projeto (BASE_DIR)
BASE_DIR = Path(__file__).resolve().parent.parent

# Adiciona a pasta 'apps' ao Python Path
# Isso permite importar 'clients' direto, ao invés de 'apps.clients'
sys.path.append(str(BASE_DIR / 'apps'))

# Carrega o arquivo .env para variáveis de ambiente
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- SEGURANÇA BÁSICA ---
SECRET_KEY = os.getenv("SECRET_KEY")

# Configuração do modo de depuração (DEBUG) baseado na variável de ambiente
DEBUG = os.getenv("DEBUG", "False") == "True"

# Configuração dos hosts permitidos (ALLOWED_HOSTS) para produção
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
# Adiciona domínios do Render automaticamente se estiverem no ambiente
if os.getenv("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.getenv("RENDER_EXTERNAL_HOSTNAME"))

# --- APLICATIVOS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps Personalizados (RN Pinturas)
]

# Configuração dos middlewares (MIDDLEWARE)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuração da URL principal (ROOT_URLCONF)
ROOT_URLCONF = 'rnpinturas.urls'

# Configuração dos templates (TEMPLATES)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Configuração da aplicação WSGI (WSGI_APPLICATION)
WSGI_APPLICATION = 'rnpinturas.wsgi.application'

# --- BANCO DE DADOS ---
USE_MYSQL = os.getenv("USE_MYSQL", "False").lower() in ("true", "1", "yes")

if USE_MYSQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- VALIDAÇÃO DE SENHA ---
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# --- INTERNACIONALIZAÇÃO ---
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- ARQUIVOS ESTÁTICOS ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Compressão e Cache para produção
if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- SEGURANÇA E COOKIES (Produção) ---
# Só ativa se DEBUG=False para não travar o localhost
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    # SECURE_SSL_REDIRECT = True # Cuidado ao ativar isso antes de ter HTTPS configurado
