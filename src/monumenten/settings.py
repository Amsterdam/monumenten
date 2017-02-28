from monumenten.settings_common import * # noqa F403
from monumenten.settings_common import INSTALLED_APPS, DEBUG
from monumenten.settings_databases import Location_key,\
    get_docker_host,\
    get_database_key,\
    OVERRIDE_HOST_ENV_VAR,\
    OVERRIDE_PORT_ENV_VAR
import os

INSTALLED_APPS += [
    'monumenten.api',
    'monumenten.dataset',
    'monumenten.importer',
    'monumenten.health',
    'monumenten.objectstore',

]

ROOT_URLCONF = 'monumenten.urls'


WSGI_APPLICATION = 'monumenten.wsgi.application'


DATABASE_OPTIONS = {
    Location_key.docker: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'monumenten'),
        'USER': os.getenv('DATABASE_USER', 'monumenten'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': 'database',
        'PORT': '5432'
    },
    Location_key.local: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'monumenten'),
        'USER': os.getenv('DATABASE_USER', 'monumenten'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': get_docker_host(),
        'PORT': '5412'
    },
    Location_key.override: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'monumenten'),
        'USER': os.getenv('DATABASE_USER', 'monumenten'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': os.getenv(OVERRIDE_HOST_ENV_VAR),
        'PORT': os.getenv(OVERRIDE_PORT_ENV_VAR, '5432')
    },
}

DATABASES = {
    'default': DATABASE_OPTIONS[get_database_key()]
}

# SWAGGER
SWAG_PATH = 'api-acc.datapunt.amsterdam.nl/monumenten/docs'

if DEBUG:
    SWAG_PATH = '127.0.0.1:8000/monumenten/docs'

SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': '0.1',
    'api_path': '/',

    'enabled_methods': [
        'get',
    ],

    'api_key': '',
    'USE_SESSION_AUTH': False,
    'VALIDATOR_URL': None,

    'is_authenticated': False,
    'is_superuser': False,

    'unauthenticated_user': 'django.contrib.auth.models.AnonymousUser',
    'permission_denied_handler': None,
    'resource_access_handler': None,

    'protocol': 'https' if not DEBUG else '',
    'base_path': SWAG_PATH,

    'info': {
        'contact': 'atlas.basisinformatie@amsterdam.nl',
        'description': 'This is the Monumenten API server.',
        'license': 'Not known yet',
        'termsOfServiceUrl': 'https://atlas.amsterdam.nl/terms/',
        'title': 'Tellus',
    },

    'doc_expansion': 'list',
}

HEALTH_MODEL = 'dataset.Monument'
