import random
import requests
import json

from django.contrib.auth.models import User
from celery import shared_task
from django.db import transaction
from django.core.management import call_command

from celery.utils.log import get_task_logger  # noqa
logger = get_task_logger(__name__)


@shared_task()
def task_test_logger():
    logger.info('test')


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 5})
def task_process_notification(self):
    if random.choice([0, 1]):
        # mimic random error
        raise Exception()

    # this would block the I/O
    requests.post('https://httpbin.org/delay/5')


@shared_task()
def task_subscribe(raw_json):
    from polls.forms import SubscribeForm
    from polls.views import subscribe_user

    form_dict = json.loads(raw_json)
    form = SubscribeForm(form_dict)
    if form.is_valid():
        subscribe_user(form.cleaned_data['email'])


@shared_task()
def task_send_welcome_email(user_pk):
    instance = User.objects.get(pk=user_pk)
    logger.info('send email to {instance.email} {instance.pk}'.format(instance=instance))


@shared_task()
def task_transaction_test():
    with transaction.atomic():
        from .views import random_username

        username = random_username()
        user = User.objects.create_user(username, 'lennon@thebeatles.com', 'johnpassword')
        user.save()
        logger.info('send email to {instance.pk}'.format(instance=user))
        raise Exception('test')


@shared_task(name='task_clear_session')
def task_clear_session():
    call_command('clearsessions')


@shared_task(bind=True)
def task_add_subscribe(self, user_pk):
    try:
        user = User.objects.get(pk=user_pk)
        requests.post(
            'https://httpbin.org/delay/5',
            data={'email': user.email},
        )
    except Exception as exc:
        raise self.retry(exc=exc)
