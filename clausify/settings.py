from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'change-me')
DEBUG = True
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes', # <--- Make sure this is here
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'summarizer', # Your local app
]

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'clausify.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',           # Add this
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',         # Add this (Fixes E402)
                'django.contrib.messages.context_processors.messages', # Add this (Fixes E404)
            ],
        },
    },
]

WSGI_APPLICATION = 'clausify.wsgi.application'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    ]
STATIC_ROOT = BASE_DIR / "staticfiles"
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')