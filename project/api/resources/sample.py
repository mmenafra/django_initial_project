# -*- coding: utf-8 -*-
from tastypie.resources import ModelResource
from api.models import Sample
from tastypie import fields
from tastypie.validation import Validation
from tastypie.authorization import Authorization

class SampleResource(ModelResource):
    class Meta:
        queryset = Comment.objects.all()
        authorization = Authorization()
        #validation = WalkValidation()
        list_allowed_methods = ['get', 'delete']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        resource_name = "sample"
        #excludes = ['created', 'id', 'user']
        include_resource_uri = True
        #include_absolute_url = True
        always_return_data = True