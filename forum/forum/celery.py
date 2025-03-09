import logging
import os

from celery import Celery

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forum.settings")

app = Celery("forum")

try:
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.autodiscover_tasks()
    logger.info("Celery tasks loaded successfully.")
except Exception as e:
    logger.error(f"Celery task discovery failed: {e}", exc_info=True)
