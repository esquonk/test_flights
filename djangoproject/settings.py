import os

import simplejson

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'tc!08-3sy^vgav$s0ylp+d4gwgjvnau%q-vsg^+t$!b!&73^+6'

DEBUG = True

INTERNAL_IPS = [
    '127.0.0.1',
]

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'debug_toolbar_alchemy',
    'django_sorcery',

    'rest_framework',
    'fares',
]

MIDDLEWARE = [
    'django_sorcery.db.middleware.SQLAlchemyMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',

]

ROOT_URLCONF = 'djangoproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'djangoproject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'flights',
        'USER': 'flights',
        'PASSWORD': 'flights',
        'ALCHEMY_OPTIONS': {
            'engine_options': {
                'json_serializer': simplejson.dumps,
                'json_deserializer': simplejson.loads,
            }
        }
    }
}

MIGRATION_MODULES = {
    'fares': None
}

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'UNAUTHENTICATED_USER': None
}

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar_alchemy.panels.sql.SQLPanel',
]

DEBUG_TOOLBAR_CONFIG = {
    'ALCHEMY_DB_ALIASES': 'djangoproject.util.get_db_dict'
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
