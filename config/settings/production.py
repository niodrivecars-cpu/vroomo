
from django.core.exceptions import ImproperlyConfigured

from .base import *

# ---- Environment validation ----
errors = []

if not SECRET_KEY:
    errors.append('SECRET_KEY must be set for production.')
elif SECRET_KEY in {'test-key-not-for-production', 'dev-insecure-key-not-for-production'}:
    errors.append('SECRET_KEY is set to a known insecure value — generate a secure key.')

if not ALLOWED_HOSTS:
    errors.append('ALLOWED_HOSTS must be configured for production.')

if DEBUG:
    errors.append('DEBUG must be False in production.')

if errors:
    raise ImproperlyConfigured(
        'Production configuration errors:\n' + '\n'.join(f'  - {e}' for e in errors)
    )

# ---- Debug ----
DEBUG = False

# ---- HTTPS & Security Headers ----
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ---- Session & CSRF cookie hardening ----
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# ---- Proxy trust (nginx terminates TLS and forwards the original scheme) ----
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ---- Session expiry ----
SESSION_COOKIE_AGE = 86_400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
