from pathlib import Path
from .settings_common import MIDDLEWARE

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = False

ALLOWED_HOSTS = ['TODO']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'ATOMIC_REQUESTS': True
    }
}

MIDDLEWARE.append('django.middleware.csrf.CsrfViewMiddleware')
