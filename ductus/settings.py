# Django settings for ductus project.

import os
DUCTUS_SITE_ROOT = os.path.dirname(__file__)
del os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

EMAIL_SUBJECT_PREFIX = '[Ductus] '

DATABASE_ENGINE = ''           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
#SECRET_KEY = 'cpoong-0a^a(kp1q0jm*(okmdmcidh_!rqjzg4&ff%93flbwr$'

# see django/conf/global_settings.py
gettext_noop = lambda s: s
LANGUAGES = (
    ('cs', 'Czech'),
    ('de', 'German'),
    ('en', 'English'),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'ductus.template_loaders.module_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.http.ConditionalGetMiddleware',
    'ductus.middleware.cache.UpdateCacheMiddleware',
    'ductus.middleware.unvarying.UnvaryingResponseMiddleware',
    'ductus.middleware.remote_addr.RemoteAddrMiddleware',
    'django.contrib.csrf.middleware.CsrfMiddleware',
    'ductus.middleware.common.DuctusCommonMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'ductus.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'ductus.urls'

TEMPLATE_DIRS = (
    DUCTUS_SITE_ROOT + '/templates',
)

LOCALE_PATHS = (
    DUCTUS_SITE_ROOT + '/locale',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'ductus.context_processors.site_settings',
    'ductus.context_processors.oldid',
    'ductus.context_processors.permissions',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.markup',
    'ductus.initialize',
    'ductus.wiki',
    'ductus.user',
    'ductus.special',
)

DUCTUS_INSTALLED_MODULES = (
    'ductus.modules.picture',
    'ductus.modules.picture_choice',
    'ductus.modules.textwiki',
)

DUCTUS_STORAGE_BACKEND = 'ductus_site.storage_backend'

DUCTUS_TRUSTED_PROXY_SERVERS = ('127.0.0.1',)

DUCTUS_MEDIA_PREFIX = '/static/ductus/'
#DUCTUS_SITE_NAME = 'Example Ductus Site'

DUCTUS_ALLOWED_LICENSES = (
    'http://creativecommons.org/licenses/publicdomain/',
    'http://creativecommons.org/licenses/by-sa/2.0/',
    'http://creativecommons.org/licenses/by-sa/2.5/',
    'http://creativecommons.org/licenses/by-sa/3.0/',
    'http://creativecommons.org/licenses/by/1.0/',
    'http://creativecommons.org/licenses/by/2.0/',
    'http://creativecommons.org/licenses/by/2.5/',
    'http://creativecommons.org/licenses/by/3.0/',
)

DUCTUS_FRONT_PAGE = '/wiki/front_page'

#DUCTUS_FLICKR_API_KEY = ""

CACHE_BACKEND = 'dummy:///'
CACHE_MIDDLEWARE_SECONDS = 86400

LOGIN_URL = '/login/'
LOGOUT_URL= '/logout/'
LOGIN_REDIRECT_URL = '/'

#DEFAULT_FROM_EMAIL = "no-reply@example.com"

try:
    from ductus_local_settings import *
except ImportError:
    pass
