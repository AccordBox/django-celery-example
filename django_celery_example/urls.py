"""django_celery_example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import polls.views

urlpatterns = [
    path('admin/', admin.site.urls),

    # webhook
    path('webhook_test', polls.views.webhook_test, name='webhook_test'),
    path('webhook_test2', polls.views.webhook_test2, name='webhook_test2'),

    path('subscribe', polls.views.subscribe, name='subscribe'),
    path('subscribe2', polls.views.subscribe2, name='subscribe2'),

    path('task_status', polls.views.task_status, name='task_status'),

    path('transaction_test', polls.views.transaction_test, name='transaction_test'),
    path('transaction_test2', polls.views.transaction_test2, name='transaction_test2'),

    path('transaction_celery', polls.views.transaction_celery, name='transaction_celery'),
    path('transaction_celery2', polls.views.transaction_celery2, name='transaction_celery2'),
    path('transaction_celery3', polls.views.transaction_celery3, name='transaction_celery3'),

    path('subscribe3', polls.views.subscribe3, name='subscribe3'),

]
