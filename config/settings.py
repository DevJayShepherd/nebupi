'''
Django settings for ready_saas project.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
'''

import environ
import os
from celery.schedules import crontab

# https://django-environ.readthedocs.io/en/latest/quickstart.html
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# False if not in os.environ because of casting above
DEBUG = env('DEBUG')

SECRET_KEY = env('SECRET_KEY')

# https://docs.djangoproject.com/en/4.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
# https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')


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

THIRD_PARTY_APPS = env.list('THIRD_PARTY_APPS')

LOCAL_APPS = [
    "ready_saas",
    "users",
    "orders",
    # "waitlist", # Optional. Uncomment if you want to include the waitlist functionality
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
            ],
        },
    },
]

# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': env.db()
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
        'SENDGRID_API_KEY': env('SENDGRID_API_KEY'),
    }

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = env('SERVER_EMAIL')


# celery

CELERY_BROKER_URL = env('REDIS_URL')
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
