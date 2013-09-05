from django.conf.urls import patterns, include, url
from tastypie.api import Api

from django.contrib import admin
admin.autodiscover()

v1_api = Api(api_name='v1')

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'quotes.views.home', name='home'),
    # url(r'^quotes/', include('quotes.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^api/', include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
)
