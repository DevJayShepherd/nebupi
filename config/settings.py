'''
Ready SaaS Source Code

Copyright 2023 Ready SaaS

Licensed under Ready SaaS Proprietary License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.readysaas.app/licenses/

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


'''
Django settings for ready_saas project.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
'''

import os
import dotenv
from celery.schedules import crontab
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Setup environment variables with fallback to .env file
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Read .env file if it exists
dotenv_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

# Get environment variables from system first, then fall back to .env file
DEBUG = os.getenv('DEBUG', env('DEBUG', default='off')) == 'on' or os.getenv('DEBUG', env('DEBUG', default=False)) is True

# Use a default SECRET_KEY if not provided in environment variables
# This is a fallback for development only, in production always set SECRET_KEY in environment variables
DEFAULT_SECRET_KEY = 'django-insecure-default-key-for-development-only-change-in-production'
SECRET_KEY = os.getenv('SECRET_KEY', env('SECRET_KEY', default=DEFAULT_SECRET_KEY))

# https://docs.djangoproject.com/en/4.2/ref/settings/#allowed-hosts
# Default to localhost and 127.0.0.1 if no ALLOWED_HOSTS is provided
DEFAULT_ALLOWED_HOSTS = ['localhost', '127.0.0.1']
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else env.list('ALLOWED_HOSTS', default=DEFAULT_ALLOWED_HOSTS)
# https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
# Default to empty list if no CSRF_TRUSTED_ORIGINS is provided
DEFAULT_CSRF_TRUSTED_ORIGINS = []
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if os.getenv('CSRF_TRUSTED_ORIGINS') else env.list('CSRF_TRUSTED_ORIGINS', default=DEFAULT_CSRF_TRUSTED_ORIGINS)


# Application definition
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    "django_celery_results",
    "django_celery_beat",
]

if DEBUG:
    THIRD_PARTY_APPS += [
        "django_extensions",
        "django_browser_reload",
    ]

LOCAL_APPS = [
    "ready_saas",
    "users",
    "orders",
    "waitlist",  # Optional. Comment out if you want to exclude the waitlist functionality
    "blog",  # Optional. Comment out if you want to exclude the blog functionality
    # Your stuff: custom apps go here
]

# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
# MIGRATION_MODULES = {"sites": "ready_saas.contrib.sites.migrations"}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE += [
        'django_browser_reload.middleware.BrowserReloadMiddleware',
    ]


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'users', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.is_debug',  # custom context processor to differentiate between dev and prod
                'config.context_processors.ga_tracking_id',  # custom context processor for Google Analytics
            ],
        },
    },
]

# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Use DATABASE_URL from system environment if available, otherwise use the one from .env
# Default to SQLite if no DATABASE_URL is provided
DEFAULT_DATABASE_URL = 'sqlite:///db.sqlite3'
database_url = os.getenv('DATABASE_URL', env('DATABASE_URL', default=DEFAULT_DATABASE_URL))
DATABASES = {
    'default': env.db_url('DATABASE_URL', default=database_url)
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Users
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# Login via email link (django-sesame)
# https://django-sesame.readthedocs.io/en/stable/tutorial.html
SESAME_MAX_AGE = 600
AUTHENTICATION_BACKENDS += [
    "sesame.backends.ModelBackend"
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = BASE_DIR + "/staticfiles"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email
# https://docs.djangoproject.com/en/4.2/topics/email/

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'anymail.backends.sendgrid.EmailBackend'
    ANYMAIL = {
        'SENDGRID_API_KEY': os.getenv('SENDGRID_API_KEY', env('SENDGRID_API_KEY', default='')),
    }

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', env('DEFAULT_FROM_EMAIL', default='noreply@example.com'))
SERVER_EMAIL = os.getenv('SERVER_EMAIL', env('SERVER_EMAIL', default='server@example.com'))


# celery

# Default to a local Redis instance if no REDIS_URL is provided
DEFAULT_REDIS_URL = 'redis://localhost:6379'
CELERY_BROKER_URL = os.getenv('REDIS_URL', env('REDIS_URL', default=DEFAULT_REDIS_URL))
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_RESULT_EXTENDED = True

CELERY_BEAT_SCHEDULE = {
    'monitor-subscriptions-every-day': {
        'task': 'Monitor Subscriptions',
        'schedule': crontab(hour=11, minute=0),
        'args': (),
    },
}


# Payments
# required setting for Paypal popup to work as desired
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'
