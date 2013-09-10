from django.test import TestCase
from django.test import Client as DjangoClient
from django.test.client import MULTIPART_CONTENT, BOUNDARY
from django.test.client import encode_multipart, FakePayload
from django.utils.http import urlencode
from urlparse import urlparse
from django.core import mail
from django.utils import simplejson
from django.core.cache import cache
from datetime import datetime
from tastypie.resources import Resource
from tastypie import http

from django.core.serializers import json

def extended_response(method):
    def wrapped(*args, **kwargs):
        start = datetime.now()
        response = method(*args, **kwargs)
        response.crono_end = datetime.now()
        response.crono_start = start
        return response
    return wrapped

"""
Extends the django client to add patch method support and
    makes it easier to send/receive json data'
"""
class Client(DjangoClient):

    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)

    def login(self, user=None, **kwargs):
        if len(kwargs) == 0 and user is not None:
            """
            return super(Client, self).login(
                username=user.user.username,
                password=user.user.password)

            This was not going to work. user.user.password is hashed.
            Replicating behavior from django.test.Client login.
            """
            return False
        else:
            return super(Client, self).login(**kwargs)

    def _path_or_resource(self, path, obj=None):
        '''If passed a Resource object, will return its URI.
           If passed a path, will return the path unmodified'''

        if isinstance(path, Resource):
            if obj is not None:
                return path.get_resource_uri(obj)
            else:
                return path.get_resource_list_uri()
        else:
            return path

    def patch_request(
            self, path, data=False,
            content_type=MULTIPART_CONTENT, **extra):

        "Construct a PATCH request."

        data = data or {}

        if content_type is MULTIPART_CONTENT:
            post_data = encode_multipart(BOUNDARY, data)
        else:
            post_data = data

        # Make `data` into a querystring only if it's not already a string. If
        # it is a string, we'll assume that the caller has already encoded it.
        query_string = None
        if not isinstance(data, basestring):
            query_string = urlencode(data, doseq=True)

        parsed = urlparse(path)
        request_params = {
            'CONTENT_LENGTH': len(post_data),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      self._get_path(parsed),
            'QUERY_STRING':   query_string or parsed[4],
            'REQUEST_METHOD': 'PATCH',
            'wsgi.input':     FakePayload(post_data),
        }
        request_params.update(extra)
        return self.request(**request_params)

    @extended_response
    def patch(
            self, path, data=None, follow=False,
            content_type="application/json", parse="json", **extra):

        """
        Send a resource patch to the server using PATCH.
        """

        data = data or {}
        path = self._path_or_resource(path, data)

        if type(data) == dict and content_type == "application/json":
            data = simplejson.dumps(data, cls=json.DjangoJSONEncoder)

        response = self.patch_request(
            path, data=data,
            content_type=content_type, **extra)

        if parse == "json":
            try:
                response.data = simplejson.loads(response.content)
            except:
                response.data = None

        if follow:
            response = self._handle_redirects(response, **extra)
        return response

    def parse(self, response, parse="json"):
        if parse == "json":
            try:
                response.data = simplejson.loads(response.content)
            except:
                response.data = None
        return response

    @extended_response
    def post(
            self, path, data=None, content_type='application/json',
            follow=False, parse='json', **extra):
        """
        Overloads default Django client POST request to setdefault content
        type to applcation/json and automatically sets data to a raw json
        string.
        """

        path = self._path_or_resource(path)
        data = data or {}

        if type(data) == dict and content_type == "application/json":
            data = simplejson.dumps(data, cls=json.DjangoJSONEncoder)


        response = super(Client, self).post(
            path, data, content_type,
            follow=False, **extra)

        if parse == "json":
            try:
                response.data = simplejson.loads(response.content)
            except:
                response.data = None
        return response

    @extended_response
    def put(
            self, path, data=None, content_type='application/json',
            follow=False, parse='json', **extra):
        """
        Overloads default Django client PUT request to setdefault content type
        to applcation/json and automatically sets data to a raw json string.
        """

        path = self._path_or_resource(path, data)
        data = data or {}

        if type(data) == dict:
            data = simplejson.dumps(data, cls=json.DjangoJSONEncoder)

        response = super(Client, self).put(path, data, content_type, **extra)

        if parse == "json":
            try:
                response.data = simplejson.loads(response.content)
            except:
                response.data = None
        return response

    @extended_response
    def delete(self, path, follow=False, obj=None, **extra):
        """
        Overloads default Django client DELETE request to setdefault content type
        to applcation/json and automatically sets data to a raw json string.
        """

        path = self._path_or_resource(path, obj)
        return super(Client, self).delete(path, **extra)

    @extended_response
    def get(self, path, data=None, follow=False, parse='json', obj=None, **extra):
        """
        Overloads default Django client GET request to receive a parse
        parameter. When parse='json', the server's response is parsed using
        simplejson and loaded into request.data.
        """

        path = self._path_or_resource(path, obj)
        data = data or {}
        response = super(Client, self).get(path, data, follow, **extra)

        if parse == "json":
            try:
                response.data = simplejson.loads(response.content)
            except Exception:
                response.data = None
        return response

    def rpc(self, method, **kwargs):
        """
        Issues a POST request using the JSONRPC 2.0 specification.
        """

        post_data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": kwargs,
            "id": 1,
        }

        return self.post("/api/rpc/", post_data, parse='json')

"""
Custom TestCase with custom methods for testing Tastypie with ease
"""
class ApiTestCase(TestCase):

    """
    Http status codes 
    """
    HTTP_STATUS_OK = 200
    HTTP_STATUS_CREATED = 201
    HTTP_STATUS_CREATED_NO_CONTENT = 204
    HTTP_STATUS_UNAUTHORIZED = 401
    HTTP_STATUS_BAD_REQUEST = 400
    HTTP_STATUS_NOT_FOUND = 404
    HTTP_STATUS_SERVER_ERROR = 500
    HTTP_STATUS_METHOD_NOT_ALLOWED = 405

    def setUp(self):
        """
        Setup for each test sets override for client and clears cache
        """
        self.client = Client()
        cache.clear()

    """
    Method to check a status code against a response object
    """
    def assertResponseHasStatus(self, response, status, msg=None):
        if msg is None:
            msg = response.content
        self.assertEquals(status, response.status_code, msg)

    """
    Method that checks a response object for a specific content-type
    """
    def assertResponseHasContentType(self, response, expected_content_type):
        header, content_type = response._headers['content-type']
        content_type = content_type.split(";")[0]
        self.assertEquals(expected_content_type, content_type)

    """
    Method that check if response is a 405
    """
    def assertResponseIsMethodNotAllowed(self, response):
        self.assertEqual(405, response.status_code, response.content)

    """
    Method that check if response is a 401
    """
    def assertResponseIsMethodUnAuthorized(self, response):
        self.assertEqual(401, response.status_code, response.content)

    """
    Method that check if response is a 200
    """
    def assertResponseIsOk(self, response):
        self.assertEqual(200, response.status_code, response.content)

    """
    Method that check if response is a 204
    """
    def assertResponseIsOkNoContentReturned(self, response):
        self.assertEqual(204, response.status_code, response.content)

    """
    Method that check if response is a 201
    """
    def assertResponseIsCreated(self, response):
        self.assertEqual(201, response.status_code, response.content)

    """
    Method that check if response is a 400
    """
    def assertResponseIsClientError(self, response):
        self.assertTrue(400 <= response.status_code <= 499, response.content)

    """
    Assert function to check that a tastypie json response
        has a given count of objects
    """
    def assertResponseHasObjectCount(self, response, count):
        if response.data:
            data = response.data
            self.assertEqual(
                data.get('meta', {}).get('total_count', {}), count,
                response.content)
        else:
            self.assertTrue(False, response.content)

    """
    Method that created a given user and logs him in
    """
    def create_user_and_login(self, email=None, password='password', force=None, client_version=None):
        force = force or { 'previous_session' : datetime.now()}
        if email:
            force['email'] = email
        if password:
            force['password'] = password
        if client_version:
            force['client_version'] = client_version

        userprofiles = tastyfactory["userprofile"]
        (location, profile) = userprofiles.create(**force)
        self.client.login(username=profile.email, password=force['password'])
        return location, profile

    """
    Assetion method that checks if a repsonse has a specific error name
    """
    def assertResponseHasError(self, response, error_name, **kwargs):
        try:
            errors = self.__response_get_errors(response)
            msg = "Expecting %s error response, but got only: %s"
            msg %= (error_name, errors)
            self.assertTrue(
                self.__response_has_error(response, error_name, **kwargs), msg)
        except Exception:
            msg = "Malformed error response: %s" % repr(response.content)
            self.assertTrue(False, msg)

    """
    internal private function of our testCase
    """
    def __format_error(self, error_desc):
        args_list = ['%s=%s' % (key, value) for (key, value) in error_desc['args'].items()]
        return "%s(%s)" % (error_desc['name'], ', '.join(args_list))

    """
    internal private function of our testCase
    """
    def __response_get_errors(self, response):
        errors = []
        if response.__class__ != http.HttpBadRequest:
            raise Exception()
        for error_desc in [inner for outer in response.data.values() for inner in outer]:
            errors.append(self.__format_error(error_desc))

        return errors

    """
    internal private function of our testCase
    """
    def __response_has_error(self, response, error_name, **kwargs):
        try:
            for error_desc in [inner for outer in response.data.values() for inner in outer]:
                same_name = error_desc['name'] == error_name
                same_args = kwargs == error_desc['args']

                if same_name and same_args:
                    return True
        except Exception:
            msg = "Malformed error response: %s" % repr(response.content)
            self.assertTrue(False, msg)

        return False
