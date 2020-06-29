from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase, override_settings
from celery.exceptions import Retry
from unittest.mock import patch
from polls.tasks import task_add_subscribe
from polls.factories import UserFactory


class SubscribeTestCase(TransactionTestCase):

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @patch('polls.views.requests.post')
    def test_subscribe3_post_succeed(self, mock_requests_post):
        """
        Check form validation
        """
        response = self.client.post(
            reverse('subscribe3'),
            {
                'name': 'test',
                'email': 'test@email.com',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.filter(username='test').exists(), True)

        mock_requests_post.assert_called_with(
            'https://httpbin.org/delay/5',
            data={'email': 'test@email.com'}
        )


class SubscribeViewTestCase2(TestCase):
    """
    This class only test Django view
    """
    @patch('polls.views.task_add_subscribe.delay')
    def test_subscribe3_post_succeed(self, mock_task_add_subscribe_delay):
        # https://github.com/adamchainz/django-capture-on-commit-callbacks
        from django_capture_on_commit_callbacks import capture_on_commit_callbacks

        with capture_on_commit_callbacks(execute=True) as callbacks:
            response = self.client.post(
                reverse('subscribe3'),
                {
                    'name': 'test',
                    'email': 'test@email.com',
                }
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.filter(username='test').exists(), True)

        # check callbacks
        self.assertEqual(len(callbacks), 1)

        user = User.objects.filter(username='test').first()
        mock_task_add_subscribe_delay.assert_called_with(
            user.pk
        )


class TaskAddSubscribeTest(TestCase):
    """
    Only test the Celery task
    """

    @patch('polls.tasks.requests.post')
    def test_post_succeed(self, mock_requests_post):
        instance = UserFactory.create()
        task_add_subscribe(instance.pk)

        mock_requests_post.assert_called_with(
            'https://httpbin.org/delay/5',
            data={'email': instance.email}
        )

    @patch('polls.tasks.task_add_subscribe.retry')
    @patch('polls.views.requests.post')
    def test_exception(self, mock_requests_post, mock_task_add_subscribe_retry):
        mock_task_add_subscribe_retry.side_effect = Retry()
        mock_requests_post.side_effect = Exception()

        instance = UserFactory.create()

        with self.assertRaises(Retry):
            task_add_subscribe(instance.pk)
