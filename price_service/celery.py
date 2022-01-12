from __future__ import absolute_import
import os

from django.conf import settings
from celery import Celery
from celery.schedules import crontab


# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "price_service.settings")
app = Celery("price_service")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.conf.beat_schedule = {
    "check_price_results": {
        "task": "price_service_api.tasks.price_check",
        "schedule": crontab(minute="0", hour=f"*/{settings.RESPONSE_WAIT_TIME}"),
        "args": (),
    },
}
app.conf.timezone = "UTC"
