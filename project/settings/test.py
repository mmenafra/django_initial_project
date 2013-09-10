from base import *

########## TEST SETTINGS
TEST_RUNNER = 'discover_runner.DiscoverRunner'
TEST_DISCOVER_TOP_LEVEL = SITE_ROOT
TEST_DISCOVER_ROOT = SITE_ROOT
TEST_DISCOVER_PATTERN = "test*.py"

########## IN-MEMORY TEST DATABASE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        'NAME': normpath(join(DJANGO_ROOT, 'default.db')),
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}