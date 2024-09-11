from .settings_base import *
import os
JWT_EXPIRATION_TIME = 172800
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = [
    'https://afghangallery.mehdiwahid.dev'
]
SECRET_KEY = os.getenv("SECRET_KEY")

SIMPLE_JWT["SIGNING_KEY"] =  SECRET_KEY

DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3"
    }
}
