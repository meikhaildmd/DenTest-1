"""
Django settings for myproject project.
"""

import os
from pathlib import Path
import environ
import dj_database_url

# --- BASE DIR ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- ENV SETUP ---
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# --- SECURITY ---
SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-me")
DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=[
        # ✅ Main brand
        "toothprep.com",
        "www.toothprep.com",
        "api.toothprep.com",
        # ✅ Alternate domains
        "odontest.com",
        "www.odontest.com",
        "dentest.net",
        "www.dentest.net",
        "dentestpro.com",
        "www.dentestpro.com",
        # ✅ Render fallback
        "toothprep-backend.onrender.com",
        "localhost",
        "127.0.0.1",
    ],
)

# --- APPLICATIONS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'quiz',
    'debug_toolbar',
    "rest_framework",
    "corsheaders",
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'myproject.core.urls'

# --- TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'templates'],
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

WSGI_APPLICATION = 'myproject.core.wsgi.application'

# --- DATABASE ---

if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ['DATABASE_URL'],
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- REST FRAMEWORK ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# --- TIME + LANGUAGE ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- FILES ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- INTERNALS ---
INTERNAL_IPS = ['127.0.0.1']
LOGIN_REDIRECT_URL = 'classification_list'

# --- LOGGING ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# --- CORS + CSRF (Production Safe) ---

CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_NAME = "csrftoken"

# ✅ Must be 'None' (not 'Lax') so cookies can cross from toothprep.com → Render backend
CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SAMESITE = "None"

# ✅ Always True in production (HTTPS only)
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    # Local dev
    "http://localhost:3000",
    "http://127.0.0.1:3000",

    # Live domains
    "https://toothprep.com",
    "https://www.toothprep.com",
    "https://odontest.com",
    "https://www.odontest.com",
    "https://dentest.net",
    "https://www.dentest.net",
    "https://dentestpro.com",
    "https://www.dentestpro.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://toothprep.com",
    "https://www.toothprep.com",
    "https://odontest.com",
    "https://www.odontest.com",
    "https://dentest.net",
    "https://www.dentest.net",
    "https://dentestpro.com",
    "https://www.dentestpro.com",
    # ✅ Include backend itself
    "https://toothprep-backend.onrender.com",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-language",
    "content-language",
    "content-type",
    "authorization",
    "x-csrftoken",
    "x-requested-with",
]

# --- SECURITY HEADERS ---
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG