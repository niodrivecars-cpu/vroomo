import os
from pathlib import Path

import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY', default='dev-insecure-key-not-for-production')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_bootstrap5',
    'fleet',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'fleet.middleware.CompanyMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'fleet.middleware.RateLimitLogMiddleware',
    'fleet.middleware.SecurityHeadersMiddleware',
]

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

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
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    DATABASES = {
        'default': dict(dj_database_url.parse(DATABASE_URL, conn_max_age=600, conn_health_checks=True)),
    }
else:
    DATABASES = {
        'default': dict(dj_database_url.parse(
            f"postgres://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}",
            conn_max_age=600,
            conn_health_checks=True,
        )),
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = config('LANGUAGE_CODE', default='en')
TIME_ZONE = config('TIME_ZONE', default='Africa/Casablanca')

USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
    ('ar', 'العربية'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = config('STATIC_ROOT', default=str(BASE_DIR / 'staticfiles'))

MEDIA_URL = 'media/'
MEDIA_ROOT = config('MEDIA_ROOT', default=str(BASE_DIR / 'media'))

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CACHE_URL = config('CACHE_URL', default='')
if CACHE_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': CACHE_URL,
            'KEY_PREFIX': 'vroom',
            'TIMEOUT': 300,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

SECURITY_RATE_LIMITS = {
    'login_ip': '5/m',
    'login_user': '20/h',
    'password_reset': '3/h',
    'upload_per_user': '10/m',
    'upload_per_hour': '50/h',
    'api': '30/m',
    'download_per_user': '20/h',
    'download_anon_ip': '10/h',
}

DOCUMENT_SIGNED_URL_TTL = config('DOCUMENT_SIGNED_URL_TTL', default=24 * 60 * 60, cast=int)

LOG_LEVEL = config('LOG_LEVEL', default='INFO')
LOG_DIR = config('LOG_DIR', default='')

_log_formatters = {
    'verbose': {
        'format': '{levelname} {asctime} {name} {message}',
        'style': '{',
    },
}
_log_handlers = {
    'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',
    },
}
if LOG_DIR:
    os.makedirs(LOG_DIR, exist_ok=True)
    _log_handlers['file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': os.path.join(LOG_DIR, 'vroom.log'),
        'maxBytes': 10 * 1024 * 1024,
        'backupCount': 5,
        'formatter': 'verbose',
    }
_log_handler_names = list(_log_handlers)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': _log_formatters,
    'handlers': _log_handlers,
    'root': {'handlers': _log_handler_names, 'level': LOG_LEVEL},
    'loggers': {
        'django.request': {'handlers': _log_handler_names, 'level': 'ERROR', 'propagate': False},
        'vroom.ratelimit': {'handlers': _log_handler_names, 'level': 'WARNING', 'propagate': False},
    },
}

SECURITY_CSP = {
    'default-src': "'self'",
    'script-src': ["'self'", 'https://cdn.jsdelivr.net'],
    'style-src': ["'self'", "'unsafe-inline'", 'https://cdn.jsdelivr.net'],
    'img-src': ["'self'", 'data:'],
    'font-src': "'self'",
    'connect-src': "'self'",
    'frame-ancestors': "'none'",
    'base-uri': "'self'",
    'form-action': "'self'",
}

ADMIN_EMAIL = config('ADMIN_EMAIL', default='admin@vroom.local')
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=30, cast=int)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=f'Vroom <{EMAIL_HOST_USER}>')
SERVER_EMAIL = config('SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)
