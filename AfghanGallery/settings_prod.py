from settings_base import *
import os
DEBUG = False
SECRET_KEY = os.getenv("SECRET_KEY")
allowed_hosts = []
for host in os.getenv("ALLOWED_HOST").split(","):
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
