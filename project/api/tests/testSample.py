# -*- coding: utf-8 -*-
from .factories import *
from base import ApiTestCase
from api.application import api
from api.models import Sample
from mockups import tastyfactory

samples = api._registry["sample"]

class SampleTestCase(ApiTestCase):

    @classmethod
    def setUpClass(cls):
        super(SampleTestCase, cls).setUpClass()

        sample = SampleFactory.create()

        cls.sample_uri, cls.sample = tastyfactory['sample'].create()

    def test_get_ok(self):

        response = self.client.get(samples.get_resource_uri())
        
        self.assertResponseHasObjectCount(response, 2)
        self.assertResponseIsOk(response)
