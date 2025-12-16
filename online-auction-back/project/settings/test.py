"""
Django test settings.

These settings are used when running tests.
"""

from .base import *

DEBUG = False

# Use a faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Database - Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Email - Use in-memory backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable Huey task queue (run tasks synchronously)
HUEY = {
    'huey_class': 'huey.RedisHuey',
    'name': 'auction-test',
    'url': 'redis://localhost:6379',
    'immediate': True,  # Run tasks immediately in tests
}

# Use in-memory channel layer for tests
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
        'level': 'CRITICAL',
    },
}

# Media files for tests
MEDIA_ROOT = BASE_DIR / 'test_media'
