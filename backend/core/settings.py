"""
Django settings for core project - YOJNAVIA.
"""

from pathlib import Path
import os
import sys
import dj_database_url
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Add backend directory to sys.path so 'apps.xyz' imports cleanly
sys.path.insert(0, str(BASE_DIR))

# Load .env file
load_dotenv(BASE_DIR / '.env')


def _env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def _env_list(name, default=''):
    return [item.strip() for item in os.getenv(name, default).split(',') if item.strip()]


DEBUG = _env_bool('DEBUG', default=False)

# SECRET_KEY must come from the environment. A clearly-named dev-only fallback
# is allowed ONLY when DEBUG is true.
DEV_ONLY_FALLBACK_SECRET_KEY = 'DEV-ONLY-INSECURE-FALLBACK-KEY-NEVER-USE-IN-PRODUCTION'
SECRET_KEY = os.getenv('SECRET_KEY', '')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = DEV_ONLY_FALLBACK_SECRET_KEY
    else:
        raise ImproperlyConfigured('SECRET_KEY environment variable is required when DEBUG is False.')

ALLOWED_HOSTS = ['*'] if DEBUG else _env_list(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,testserver,.onrender.com,.railway.app,.koyeb.app,yojna-via.vercel.app'
)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'corsheaders',
    'rest_framework',

    # Yojnavia core apps
    'apps.profiles',
    'apps.schemes',
    'apps.citizens',
    'apps.eligibility_engine',
    'apps.eligibility',
    'apps.documents',
    'apps.ai_assistant',
    'apps.tracker',
    'apps.notifications',
    'apps.counselor',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Top of middleware for CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

try:
    import whitenoise  # noqa: F401
    MIDDLEWARE.insert(2, 'whitenoise.middleware.WhiteNoiseMiddleware')
except ImportError:
    pass

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# Default: SQLite (existing db.sqlite3) when DATABASE_URL is unset; set DATABASE_URL to use PostgreSQL.
_db_env = os.environ.get("DATABASE_URL", "").strip()
_default_db_url = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
DATABASES = {
    'default': dj_database_url.parse(_db_env or _default_db_url, conn_max_age=600)
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# In-Memory High Performance Cache for Schemes and Document Dependency Graphs
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'yojnavia-mem-cache',
        'TIMEOUT': 300,  # 5 minutes default TTL
    }
}

# REST Framework Configuration with Throttling and Security
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '120/min',
        'user': '600/min',
        'ai_intake': '30/min',
        'voice_intake': '15/min',
        'counselor': '120/min',
    },
}

# CORS settings for frontend SPA (Vercel + Local dev)
_default_cors = (
    'http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,'
    'https://yojna-via.vercel.app'
)
CORS_ALLOWED_ORIGINS = _env_list('CORS_ALLOWED_ORIGINS', _default_cors)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = _env_bool('CORS_ALLOW_ALL', default=False)

CSRF_TRUSTED_ORIGINS = _env_list(
    'CSRF_TRUSTED_ORIGINS',
    'https://yojna-via.vercel.app,http://localhost:5173,http://127.0.0.1:5173'
)

# Production Security & Proxy Headers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
