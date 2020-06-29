"""
xunit-style tests
"""

import pytest
from unittest import mock

from celery.exceptions import Retry

import requests

from polls.tasks import task_add_subscribe
from polls.factories import UserFactory


@pytest.mark.usefixtures('db')
class TestTaskAddSubscribe:

    def setup(self):
        pass

    def teardown(self):
        pass

    @mock.patch('polls.tasks.requests.post')
    def test_post_succeed(self, mock_requests_post):
        instance = UserFactory.create()
        task_add_subscribe(instance.pk)

        mock_requests_post.assert_called_with(
            'https://httpbin.org/delay/5',
            data={'email': instance.email}
        )

    @pytest.mark.usefixtures('db')
    @mock.patch('polls.tasks.task_add_subscribe.retry')
    @mock.patch('polls.views.requests.post')
    def test_exception(self, mock_requests_post, mock_task_add_subscribe_retry):
        mock_task_add_subscribe_retry.side_effect = Retry()
        mock_requests_post.side_effect = Exception()

        instance = UserFactory.create()

        with pytest.raises(Retry):
            task_add_subscribe(instance.pk)
