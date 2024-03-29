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
import django
from django.utils.encoding import smart_str
django.utils.encoding.smart_text = smart_str

from Config import Config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

AWS_ACCESS_KEY_ID = Config.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = Config.AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = Config.AWS_STORAGE_BUCKET_NAME
AWS_S3_ENDPOINT_URL = Config.AWS_S3_ENDPOINT_URL
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = Config.AWS_LOCATION
STATIC_URL = '%s/%s' % (AWS_S3_ENDPOINT_URL, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{PUBLIC_MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'necrotopia.storage_backends.PublicMediaStorage'
PRIVATE_MEDIA_LOCATION = 'private'
PRIVATE_FILE_STORAGE = 'necrotopia.storage_backends.PrivateMediaStorage'


STATICFILES_DIRS = (BASE_DIR / 'static',)


TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = Config.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = Config.DEBUG

AUTH_USER_MODEL = 'necrotopia.UserProfile'

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
    'crispy_forms',
    'crispy_bootstrap5',
    'django_password_validators',
    'django_password_validators.password_history',
    'django_bootstrap_icons',
    'tagging',
    'storages',
    'necrotopia',
]

# url to redirect after successful login
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

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

EMAIL_USE_TLS = Config.EMAIL_USE_TLS
EMAIL_HOST = Config.EMAIL_HOST
EMAIL_HOST_USER = Config.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = Config.EMAIL_HOST_PASSWORD
EMAIL_PORT = Config.EMAIL_PORT

EMAIL_BACKEND = Config.EMAIL_BACKEND
# EMAIL_FILE_PATH = '/tmp/messages'  # change this to a proper location

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
    {
        'NAME': 'django_password_validators.password_history.password_validation.UniquePasswordsValidator',
        'OPTIONS': {
            # How many recently entered passwords matter.
            # Passwords out of range are deleted.
            # Default: 0 - All passwords entered by the user. All password hashes are stored.
            'last_passwords': 5  # Only the last 5 passwords entered by the user
        }
    },
    {
        'NAME': 'django_password_validators.password_character_requirements.password_validation.PasswordCharacterValidator',
        'OPTIONS': {
            'min_length_digit': 1,
            'min_length_alpha': 1,
            'min_length_special': 1,
            'min_length_upper': 1,
            'special_characters': "~!@#$%^&*()_+{}\":;'[]"
        }
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

# django-resized settings
DJANGORESIZED_DEFAULT_SIZE = [1920, 1080]
DJANGORESIZED_DEFAULT_SCALE = 0.5
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
# DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'JPEG': ".jpg"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True


print("STATIC_URL {static_folder}".format(static_folder=STATIC_URL))
print("MEDIA_URL {static_folder}".format(static_folder=MEDIA_URL))
print("STATICFILES_DIR {static_folder}".format(static_folder=STATICFILES_DIRS))
print("ALLOWED HOSTS {allowed_hosts}".format(allowed_hosts=ALLOWED_HOSTS))
print("DEBUG {debug}".format(debug=Config.DEBUG))
if Config.DEBUG:
    print("DB {host}:{port}".format(host=Config.DB_HOST_IP, port=Config.DB_HOST_PORT))
