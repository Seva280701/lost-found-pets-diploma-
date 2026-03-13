"""
Django settings for Lost and Found Pets platform (Latvian Animal Shelter Integration).
Bachelor thesis project.
"""
import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

# SECURITY: keep the secret key in environment in production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Local apps (shelters before reports — reports.models imports Shelter)
    'accounts',
    'core',
    'shelters',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database — PostgreSQL (recommended) or SQLite for local dev.
# Priority:
# 1) If DATABASE_URL is set (e.g. on Render), parse it.
# 2) Else if USE_POSTGRES=1, use individual DB_* env vars.
# 3) Else fall back to SQLite.
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Basic URL parsing without extra dependencies
    from urllib.parse import urlparse

    parsed = urlparse(database_url)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path.lstrip('/') or 'lostfound_pets',
            'USER': parsed.username or '',
            'PASSWORD': parsed.password or '',
            'HOST': parsed.hostname or 'localhost',
            'PORT': str(parsed.port or '5432'),
        }
    }
elif os.environ.get('USE_POSTGRES', '').lower() in ('1', 'true', 'yes'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'lostfound_pets'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en'
TIME_ZONE = 'Europe/Riga'
USE_I18N = True
USE_TZ = True

# Supported languages: English, Latvian, Russian
LANGUAGES = [
    ('en', 'English'),
    ('lv', 'Latviešu'),
    ('ru', 'Русский'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login redirects
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'

# Email (for password reset). Console backend prints to terminal in dev.
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@lostfound-pets.local')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Google Maps (set in .env for production)
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

# Role constants (Django Groups names)
ROLE_USER = 'user'
ROLE_SHELTER = 'shelter'
ROLE_ADMIN = 'admin'
