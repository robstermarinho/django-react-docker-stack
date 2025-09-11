from .settings import *

# Database - Use SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # In-memory
    }
}

# Allow all hosts for testing
ALLOWED_HOSTS = ["*"]


# Speed up password hashing in tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
