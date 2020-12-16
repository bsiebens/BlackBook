"""
Django settings for django_blackbook project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "!m*akp#neme_b#hmng#*ngx+4#e6r)*948k3773!t4z$@t6ek#"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "192.168.60.25", "blackbook.siebens.org"]
INTERNAL_IPS = ["127.0.0.1", "192.168.60.25"]


# Application definition

INSTALLED_APPS = [
    "blackbook.apps.BlackbookConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "minio_storage",
    "taggit",
    "taggit_helpers",
    "djmoney",
    "djmoney.contrib.exchange",
    "django_filters",
    "corsheaders",
    "graphene_django",
    "rest_framework",
]

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = "django_blackbook.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_blackbook.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Brussels"

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_FORMAT = "%d %b %Y"
USE_THOUSAND_SEPARATOR = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"

AUTHENTICATION_BACKENDS = ["graphql_jwt.backends.JSONWebTokenBackend", "django.contrib.auth.backends.ModelBackend"]

OPEN_EXCHANGE_RATES_APP_ID = os.getenv("OPEN_EXCHANGE_RATES_APP_ID", None)
BASE_CURRENCY = "EUR"
DEFAULT_CURRENCY = BASE_CURRENCY
CURRENCIES = [
    "ALL",
    "EUR",
    "AMD",
    "AZN",
    "BYN",
    "BAM",
    "BGN",
    "HRK",
    "CZK",
    "DKK",
    "GEL",
    "HUF",
    "ISK",
    "CHF",
    "MDL",
    "MKD",
    "NOK",
    "PLN",
    "RON",
    "RUB",
    "RSD",
    "SEK",
    "TRY",
    "UAH",
    "GBP",
]

TAGGIT_CASE_INSENSTIVE = True

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = os.getenv("EMAIL_PORT", 587)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", None)
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", None)
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", True)

DEFAULT_FROM_EMAIL = os.getenv("EMAIL_HOST_USER", "admin@localhost")

if os.getenv("S3_ENABLE", False):
    DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
    STATICFILES_STORAGE = "minio_storage.storage.MinioStaticStorage"

MINIO_STORAGE_ENDPOINT = os.getenv("S3_STORAGE_ENDPOINT", None)
MINIO_STORAGE_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", None)
MINIO_STORAGE_SECRET_KEY = os.getenv("S3_SECRET_KEY", None)
MINIO_STORAGE_MEDIA_BUCKET_NAME = os.getenv("S3_BUCKET", "django-dev")
MINIO_STORAGE_STATIC_BUCKET_NAME = os.getenv("S3_BUCKET", "django-dev")

CORS_ORIGIN_ALLOW_ALL = True

GRAPHENE = {
    "SCHEMA": "blackbook.schema.schema",
    "MIDDLEWARE": [
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
    ],
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}
