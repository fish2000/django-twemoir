# Django settings for example project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

import tempfile, os, twemoir
from django import contrib
tempdata = tempfile.mkdtemp()
approot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
adminroot = os.path.join(contrib.__path__[0], 'admin')
tmroot = os.path.dirname(twemoir.__file__)

DATABASES = {
    'default': {
        'NAME': os.path.join(approot, 'twemoir-test.db'),
        'TEST_NAME': os.path.join(tempdata, 'twemoir-test.db'),
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
    }
}
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
MEDIA_ROOT = os.path.join(approot, 'face', 'media')
MEDIA_URL = '/face/'
STATIC_ROOT = os.path.join(approot, 'face', 'static')
STATIC_URL = '/staticfiles/'
ADMIN_MEDIA_PREFIX = '/admin-media/'
ROOT_URLCONF = 'example.urls'

TEMPLATE_DIRS = (
    #os.path.join(adminroot, 'templates'),
    #os.path.join(adminroot, 'templates', 'admin'),
    os.path.join(tmroot, 'templates'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    #"django.core.context_processors.i18n", this is AMERICA
    "django.core.context_processors.media",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'debug_toolbar',
    'appconf',
    'tagging',
    'twemoir',
)


## DDT config
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

def showmeyourtoolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': showmeyourtoolbar,
}

INTERNAL_IPS = ('127.0.0.1',)
