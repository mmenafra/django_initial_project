from tastypie.api import Api
from api.resources import SampleResource

api = Api(api_name='v1')
api.register(SampleResource())

