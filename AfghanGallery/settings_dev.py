from settings_base import *
JWT_EXPIRATION_TIME_SECONDS = 172800
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True

DEBUG = True

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}
