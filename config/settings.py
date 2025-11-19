import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-dyve-backend-secret-key'
DEBUG = True
ENVIRONMENT = os.getenv("DJANGO_ENV", "development").lower()
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "dyve-backend-ui3c.onrender.com",
    "dyve-6nk4.vercel.app",
    "dyve-front-git-bepo-tansanguys-projects.vercel.app",
    "dyve-oct3jb3uk-tansanguys-projects.vercel.app",
    re.compile(r".*\.vercel\.app$"),
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'drf_spectacular',
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOWED_ORIGINS = [
    "https://dyve-6nk4.vercel.app",
    "https://dyve-front-git-bepo-tansanguys-projects.vercel.app",
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https:\/\/.*vercel\.app$",
]
CORS_ALLOW_ALL_ORIGINS = ENVIRONMENT != "production"

CSRF_TRUSTED_ORIGINS = [
    "https://dyve-backend-ui3c.onrender.com",
    "https://dyve-6nk4.vercel.app",
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'DYVE API',
    'DESCRIPTION': 'DYVE — Indie Artist × Venue Matching Platform',
    'VERSION': '1.0.0',
    'SERVERS': [
        {'url': 'https://dyve-backend-ui3c.onrender.com'},
    ],
    'SCHEMA_PATH_PREFIX': '/api',
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayOperationId': True,
    },
}

print("🚀 CORS Loaded:", CORS_ALLOWED_ORIGINS)
