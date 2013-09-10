import string, random
import factory
from api import models
from django.contrib.auth.models import User

def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))


class SampleFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.Sample

    text = factory.LazyAttribute(lambda t: random_string(24))
