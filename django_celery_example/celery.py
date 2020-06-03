"""
Celery config file

https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html

"""
from __future__ import absolute_import
import time
import os
import logging
from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger

from django.conf import settings


# this code copied from manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_celery_example.settings')

app = Celery("django_celery_example")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@after_setup_logger.connect()
def logger_setup_handler(logger, **kwargs):
    """
    This show you how to customize your Celery log
    """
    # print(logging.Logger.manager.loggerDict)
    pass


@app.task
def add(x, y):
    # this is for test purpose
    time.sleep(10)
    return x / y

