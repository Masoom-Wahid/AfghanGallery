from .settings_base import *
import os
DEBUG = False
JWT_EXPIRATION_TIME = 172800

SECRET_KEY = os.getenv("SECRET_KEY")
ALLOWED_HOSTS = ["127.0.0.1"]
allowed_hosts = []
CSRF_TRUSTED_ORIGINS = [
    'https://afghangallery.mehdiwahid.dev'
]
for host in os.getenv("ALLOWED_HOST","").split(","):
    allowed_hosts.append(host)

ALLOWED_HOSTS = allowed_hosts
CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASS"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT"),
    }
}
