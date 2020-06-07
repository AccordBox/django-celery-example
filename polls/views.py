import random
from random import choice
from string import ascii_lowercase, digits
import logging
import json
import time

from django.contrib.auth.models import User
from django.db import transaction

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from polls.tasks import task_process_notification, task_subscribe, task_send_welcome_email, \
    task_transaction_test, task_add_subscribe, task_sync_user
from polls.forms import SubscribeForm

import requests

logger = logging.getLogger(__name__)


def random_username():
    username = ''.join([choice(ascii_lowercase) for i in range(5)])
    return username


@csrf_exempt
def webhook_test(request):
    if random.choice([0, 1]):
        # mimic the error
        raise Exception()

    # this would block the I/O
    requests.post('https://httpbin.org/delay/5')
    return HttpResponse('pong')


@csrf_exempt
def webhook_test2(request):
    """
    Use celery worker to handle the notification
    """
    task = task_process_notification.delay()
    logger.info(task.id)
    return HttpResponse('pong')


def subscribe_user(email):
    # code here can let us test what happen if the api call fail
    if random.choice([0, 1]):
        raise Exception('random processing error')

    # here we call 3-party api to subscribe our user
    requests.post('https://httpbin.org/delay/5')


def subscribe(request):
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            subscribe_user(form.cleaned_data['email'])
            return HttpResponse('thanks')
    else:
        form = SubscribeForm()

    return render(request, 'subscribe.html', {'form': form})


def subscribe2(request):
    if request.is_ajax() and request.method == "POST":
        raw_json = json.dumps(request.POST)
        task = task_subscribe.delay(raw_json)

        # return task_id so the js can poll the state
        return JsonResponse({
            'task_id': task.task_id,
        })
    else:
        form = SubscribeForm()
        return render(request, 'subscribe2.html', {'form': form})


def task_status(request):
    from celery.result import AsyncResult

    task_id = request.GET.get('task_id')
    if task_id:
        task = AsyncResult(task_id)
        if task.state == 'FAILURE':
            error = str(task.result)
            response = {
                'state': task.state,
                'error': error,
            }
        else:
            response = {
                'state': task.state,
            }
        return JsonResponse(response)


def transaction_test(request):
    with transaction.atomic():
        user = User.objects.create_user('john1', 'lennon@thebeatles.com', 'johnpassword')
        logger.info('create user {instance.pk}'.format(instance=user))
        raise Exception('force transaction to rollback')


@transaction.atomic
def transaction_test2(request):
    user = User.objects.create_user('john2', 'lennon@thebeatles.com', 'johnpassword')
    logger.info('create user {instance.pk}'.format(instance=user))
    raise Exception('force transaction to rollback')


@transaction.atomic
def transaction_celery(request):
    """
    Why you get DoesNotExist error in Celery worker
    """
    username = random_username()
    user = User.objects.create_user(username, 'lennon@thebeatles.com', 'johnpassword')
    logger.info('create user {instance.pk}'.format(instance=user))
    task_send_welcome_email.delay(user.pk)

    time.sleep(1)
    return HttpResponse('test')


@transaction.atomic
def transaction_celery2(request):
    """
    Solve DoesNotExist error in Celery worker
    """
    username = random_username()
    user = User.objects.create_user(username, 'lennon@thebeatles.com', 'johnpassword')
    logger.info('create user {instance.pk}'.format(instance=user))
    # we register callback functions and they would be call after transaction commit
    transaction.on_commit(lambda: task_send_welcome_email.delay(user.pk))
    transaction.on_commit(lambda: task_sync_user.delay(user.pk))

    time.sleep(1)
    return HttpResponse('test')


@transaction.atomic
def transaction_celery3(request):
    """
    How to use DB transaction in Celery task
    """
    transaction.on_commit(lambda: task_transaction_test.delay())

    return HttpResponse('test')


@transaction.atomic
def subscribe3(request):
    """
    This Django view save user email to db and send task to Celery worker
    to subscribe
    """
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            instance, flag = User.objects.get_or_create(
                username=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
            )
            transaction.on_commit(
                lambda: task_add_subscribe.delay(instance.pk)
            )
            return HttpResponseRedirect('')
    else:
        form = SubscribeForm()

    return render(request, 'subscribe.html', {'form': form})
