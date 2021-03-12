import os

BASE_DIR = os.path.dirname(__file__)

ALLOWED_HOSTS = []
AUTH_PASSWORD_VALIDATORS = []
DEBUG = False
LANGUAGE_CODE = 'en-us'
MEDIA_URL = ''
ROOT_URLCONF = 'test_settings'
SECRET_KEY = 'sosupersecret'
STATIC_URL = '/static/'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3', 
    'NAME': os.getenv('DJANGO_DB_NAME', ':memory:') 
}}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'ckeditor',
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


TEMPLATES = [{
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
}]

CKEDITOR_UPLOAD_PATH = os.path.join(BASE_DIR, 'ckeditor', 'tests', 'media')
