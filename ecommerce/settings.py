"""
Django settings for ecommerce project.
Variables sensibles en .env — no hardcodear credenciales aquí.
"""
import os
from unipath import Path

BASE_DIR = Path(__file__).ancestor(2)


# ── Cargar .env ───────────────────────────────────────────────────────────────
def load_env(env_path):
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, _, value = line.partition('=')
                os.environ[key.strip()] = value.strip()
    except FileNotFoundError:
        pass


load_env(BASE_DIR.child('.env'))


# ── Seguridad ─────────────────────────────────────────────────────────────────
SECRET_KEY    = os.environ.get('SECRET_KEY', '')
DEBUG         = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# ── Apps ──────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'applications.users',
    'applications.home',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'applications.category',
    'applications.store',
    'applications.carts',
    'applications.orders',

    'admin_thumbnails',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.child('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'applications.category.context_processors.menu_links',
                'applications.carts.context_processors.counter',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'

# ── Base de datos ─────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql_psycopg2',
        'NAME':     os.environ.get('DB_NAME',     ''),
        'USER':     os.environ.get('DB_USER',     ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST':     os.environ.get('DB_HOST',     'localhost'),
        'PORT':     os.environ.get('DB_PORT',     '5432'),
    }
}

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'users.Account'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internacionalización ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'es-pe'
TIME_ZONE     = 'America/Lima'
USE_I18N      = True
USE_L10N      = True
USE_TZ        = True

# ── Estáticos y media ─────────────────────────────────────────────────────────
STATIC_URL       = '/static/'
STATICFILES_DIRS = [BASE_DIR.child('static')]
STATIC_ROOT      = BASE_DIR.child('staticfiles')

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR.child('media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND       = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST          = os.environ.get('EMAIL_HOST',          'smtp.gmail.com')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT',      '587'))
EMAIL_USE_TLS       = os.environ.get('EMAIL_USE_TLS',       'True') == 'True'
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER',     '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# ── Mercado Pago ──────────────────────────────────────────────────────────────
MP_DEV_MODE     = os.environ.get('MP_DEV_MODE',     'True') == 'True'
MP_PUBLIC_KEY   = os.environ.get('MP_PUBLIC_KEY',   '')
MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN', '')