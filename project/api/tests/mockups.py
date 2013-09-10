from chocolate.models import ModelFactory
from chocolate.rest import TastyFactory
#from django.contrib.auth.models import User

from api import models
from api.application import api

modelfactory = ModelFactory()
#modelfactory.register(User)
modelfactory.register(models.Sample)
tastyfactory = TastyFactory(api, modelfactory)

