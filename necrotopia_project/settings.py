"""
Django settings for necrotopia_project project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

from django.template.context_processors import media

from Config import Config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIR = (
    os.path.join(BASE_DIR, 'static')
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = Config.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = Config.DEBUG

# AUTH_USER_MODEL = 'necrotopia.SystemUser'

ALLOWED_HOSTS = Config.ALLOWED_HOSTS.split(',')

GLOBAL_SITE_NAME = Config.GLOBAL_SITE_NAME

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap5',
    'imagekit',
    'nested_admin',
    'necrotopia',
]

# url to redirect after successful login
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)

ROOT_URLCONF = 'necrotopia_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':
            [
               os.path.join(BASE_DIR, 'templates'),
            ]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'necrotopia.context_processor.get_common_context',
            ],
        },
    },
]


WSGI_APPLICATION = 'necrotopia_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': Config.DB_NAME,
        'USER': Config.DB_USER,
        'PASSWORD': Config.DB_PASSWORD,
        'HOST': Config.DB_HOST_IP,
        'PORT': Config.DB_HOST_PORT,
    }
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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = Config.SERVER_TIMEZONE

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

print("STATIC_ROOT {static_folder}".format(static_folder=STATIC_ROOT))
print("STATIC_URL {static_folder}".format(static_folder=STATIC_URL))
print("STATICFILES_DIR {static_folder}".format(static_folder=STATICFILES_DIR))
print("ALLOWED HOSTS {allowed_hosts}".format(allowed_hosts=ALLOWED_HOSTS))
print("DEBUG {debug}".format(debug=Config.DEBUG))
