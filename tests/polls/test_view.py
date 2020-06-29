from unittest import mock

from django.urls import reverse
from django.contrib.auth.models import User

import pytest

import polls.tasks
from polls.factories import UserFactory


def test_subscribe3_post_succeed(db, monkeypatch, client):
    user = UserFactory.create()
    mock_task_add_subscribe_delay = mock.MagicMock(name="task_add_subscribe_delay")
    monkeypatch.setattr(polls.tasks.task_add_subscribe, 'delay', mock_task_add_subscribe_delay)

    from django_capture_on_commit_callbacks import capture_on_commit_callbacks
    with capture_on_commit_callbacks(execute=True) as callbacks:
        response = client.post(
            reverse('subscribe3'),
            {
                'name': user.username,
                'email': user.email,
            }
        )

    assert response.status_code == 302
    assert User.objects.filter(username=user.username).exists() is True

    user = User.objects.filter(username=user.username).first()
    mock_task_add_subscribe_delay.assert_called_with(
        user.pk
    )
