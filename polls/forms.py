from django import forms
from django.core import validators


class SubscribeForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
