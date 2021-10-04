"""Django settings for workbench project."""


import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DJFS = {'type': 'osfs',
        'directory_root': 'workbench/static/djpyfs',
        'url_root': '/static/djpyfs'}

DEBUG = True
if os.environ.get('EXCLUDE_SAMPLE_XBLOCKS') == 'yes':
    EXCLUDED_XBLOCKS = {
        'allscopes_demo',
        'attempts_scoreboard_demo',
        'equality_demo',
        'filethumbs',
        'helloworld_demo',
        'html_demo',
        'problem_demo',
        'sidebar_demo',
        'slider_demo',
        'textinput_demo',
        'thumbs',
        'view_counter_demo',
    }
else:
    EXCLUDED_XBLOCKS = set()

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'workbench', 'templates'),
            os.path.join(BASE_DIR, 'sample_xblocks', 'basic', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

if 'WORKBENCH_DATABASES' in os.environ:
    DATABASES = json.loads(os.environ['WORKBENCH_DATABASES'])
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'var/workbench.db'
        }
    }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
]

# Make this unique, and don't share it with anybody.
SECRET_KEY = '5ftdd9(@p)tg&amp;bqv$(^d!63psz9+g+_i5om_e%!32%po2_+%l7'

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'workbench.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'workbench.wsgi.application'

TEMPLATE_DIRS = []

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djpyfs',
    'workbench',

    # Uncomment the next line to enable the admin:
    'django.contrib.admin',

    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
]

# Only use django-debug-toolbar if it has been installed.
# Installing django-debug-toolbar before running syncdb may cause a
# DatabaseError when trying to run syncdb.
try:
    import debug_toolbar  # pylint: disable=unused-import
    INSTALLED_APPS += ('debug_toolbar',)
except ImportError:
    pass

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'var/workbench.log',
            'maxBytes': 50000,
            'backupCount': 2,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'level': 'DEBUG',
            'handlers': ['logfile'],
        }
    }
}

WORKBENCH = {
    'reset_state_on_restart': (
        os.environ.get('WORKBENCH_RESET_STATE_ON_RESTART', "false").lower() == "true"
    ),

    'services': {
        'fs': 'xblock.reference.plugins.FSService',
        'settings': 'workbench.services.SettingsService',
    }
}

try:
    from .private import *  # pylint: disable=wildcard-import,import-error,useless-suppression
except ImportError:
    pass
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
