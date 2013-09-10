from django.conf.urls import patterns, include, url
from api.application import api
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'quotes.views.home', name='home'),
    # url(r'^quotes/', include('quotes.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^api/', include(v1_api.urls)),
    (r'^docs/', include("tastydocs.urls"), {"api": api}), # api must be a reference to the TastyPie API object.
    url(r'^admin/', include(admin.site.urls)),
)
