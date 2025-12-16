"""
Django settings module.

By default, uses development settings. Set DJANGO_SETTINGS_MODULE environment
variable to use a different settings module.

Usage:
    - Development: export DJANGO_SETTINGS_MODULE=project.settings.development
    - Production: export DJANGO_SETTINGS_MODULE=project.settings.production
    - Testing: export DJANGO_SETTINGS_MODULE=project.settings.test
"""

import os

# Default to development settings
environment = os.getenv('DJANGO_ENV', 'development')

if environment == 'production':
    from .production import *
elif environment == 'test':
    from .test import *
else:
    from .development import *
