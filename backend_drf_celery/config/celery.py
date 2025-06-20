from __future__ import annotations

import os

from celery import Celery

# Default Django settings module for 'celery' CLI program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("backend_drf_celery")

# Using a string here means the worker does not have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks() 