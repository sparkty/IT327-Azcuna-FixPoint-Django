"""
WSGI config for fixpoint_backend project.

This module exposes the WSGI callable as ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fixpoint_backend.settings")

application = get_wsgi_application()
