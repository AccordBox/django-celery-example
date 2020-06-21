import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from factory import (DjangoModelFactory, Faker, LazyAttribute, LazyFunction,
                     Maybe, Sequence, SubFactory)
from factory.fuzzy import (FuzzyDateTime, FuzzyDecimal, FuzzyFloat,
                           FuzzyInteger, FuzzyText)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = FuzzyText(length=6)
    email = LazyAttribute(lambda o: '%s@example.com' % o.username)
    password = LazyAttribute(lambda o: make_password(o.username))
    first_name = FuzzyText(length=6)
    last_name = FuzzyText(length=6)
