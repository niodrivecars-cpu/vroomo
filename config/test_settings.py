import os

from .settings.base import *

# CI runs the suite against MySQL (DATABASE_URL set, mirrors production);
# local runs stay on fast in-memory SQLite.
if not os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
