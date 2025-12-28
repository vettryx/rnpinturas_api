# rnpinturas/settings.py

"""
Configurações do Django para o projeto RN Pinturas.
Baseado na estrutura moderna com Pathlib e boas práticas de produção.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# --- CONFIGURAÇÃO DE CAMINHOS ---
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / 'apps'))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- SEGURANÇA BÁSICA ---
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
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

    # --- SEGURANÇA AVANÇADA (2FA) ---
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',

    # Terceiros
    'axes',
    'storages',

    # Apps Personalizados (RN Pinturas)
    'cities',
    'clients',
    'common',
    'materials',
    'orders',
    'rooms',
    'services',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'rnpinturas.urls'

# --- TEMPLATES ---
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
            "libraries": {
                "custom_filters": "templatetags.custom_filters",
            },
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

# --- CONFIGURAÇÃO DE BACKENDS DE AUTENTICAÇÃO ---
AUTHENTICATION_BACKENDS = [
    # O Axes precisa ser o PRIMEIRO para monitorar
    'axes.backends.AxesBackend',
    # O padrão do Django para logar com usuário e senha
    'django.contrib.auth.backends.ModelBackend',
]

# --- LOGIN / LOGOUT ---
LOGIN_URL = "two_factor:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "two_factor:login"

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

# --- CONFIGURAÇÃO DE MÍDIA E UPLOAD (SFTP) ---
MEDIA_URL = os.getenv('SFTP_PUBLIC_URL', '/djangoApi_media/')

STORAGES = {
    # 1. Arquivos Estáticos (CSS/JS) - Whitenoise
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
                   if not DEBUG else "django.contrib.staticfiles.storage.StaticFilesStorage",
    },

    # 2. Arquivos de Mídia (Uploads) - SFTPStorage
    "default": {
        "BACKEND": "storages.backends.sftpstorage.SFTPStorage",
        "OPTIONS": {
            "host": os.getenv('SFTP_HOST'),
            "root_path": os.getenv('SFTP_ROOT_PATH'),
            "params": {
                "port": int(os.getenv('SFTP_PORT') or 22),
                "username": os.getenv('SFTP_USER'),
                "password": os.getenv('SFTP_PASSWORD'),
                "allow_agent": False,
                "look_for_keys": False,
            },
            "file_mode": 0o644,
        },
    },
}

# --- SEGURANÇA E SESSÃO ---
# Só ativa se DEBUG=False para não travar o localhost
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    # SECURE_SSL_REDIRECT = True

# --- SEGURANÇA CONTRA FORÇA BRUTA (AXES) ---

# Quantas chances o usuário tem antes de ser bloqueado?
AXES_FAILURE_LIMIT = 5

# Quanto tempo (em horas) ele fica bloqueado?
AXES_COOLOFF_TIME = 1

# COMO O BLOQUEIO DEVE FUNCIONAR (Sintaxe Nova)
# 'username' = Bloqueia só o usuário (padrão)
# 'ip' = Bloqueia o IP todo (afeta todo mundo naquele wifi)
# 'combination_user_and_ip' = Bloqueia aquele usuário especificamente naquele IP (Mais seguro e preciso)
AXES_LOCK_OUT_BY = 'combination_user_and_ip'

# Resetar o contador se ele acertar a senha? (Sim)
AXES_RESET_ON_SUCCESS = True

# Mensagem de erro que aparece para o usuário (Opcional, mas boa prática)
AXES_LOCKOUT_TEMPLATE = None # Usa o padrão do Django ou define um template seu depois
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]
