# Django settings for shakal project.

import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
	('Miroslav Bendik', 'mireq@linuxos.sk'),
)
DEFAULT_FROM_EMAIL = 'mireq@linuxos.sk'

MANAGERS = ADMINS

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': 'shakal.db',
		'USER': '',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	}
}

TIME_ZONE = 'Europe/Bratislava'
LANGUAGE_CODE = 'sk'
LANGUAGES = (('sk', 'Slovak'),)
TEMPLATES = (('desktop', ('default', 'bootstrap'),),)

SITE_ID = 1

USE_I18N = True
USE_L10N = True
LOCALE_PATHS = (os.path.join(ROOT, 'shakal', 'locale'), )
USE_TZ = False

MEDIA_ROOT = os.path.abspath(os.path.join(ROOT, 'media'))
MEDIA_URL = '/media/'

MEDIA_CACHE_DIR = os.path.join(MEDIA_ROOT, 'cache')
MEDIA_CACHE_URL = MEDIA_URL + 'cache/'
TEMPLATE_CACHE_DIR = os.path.join(ROOT, 'templates', 'cache')

STATIC_ROOT = ''
STATIC_URL = '/static/'

LOGIN_URL = '/profil/prihlasit/'

STATICFILES_DIRS = (
	os.path.join(ROOT, 'static'),
)

STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	#'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = 'c)vwu21d)0!pi67*_@xyv3qp!*74w50!7795t*!d9rfdu(%8g$'

TEMPLATE_LOADERS = (
	'shakal.template_dynamicloader.loader_filesystem.Loader',
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
	#'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.static',
	'django.core.context_processors.request',
	'django.contrib.auth.context_processors.auth',
	'django.contrib.messages.context_processors.messages',
	'shakal.template_dynamicloader.context_processors.style',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'auth_remember.middleware.AuthRememberMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware', # required for template_dynamicloader
	'shakal.template_dynamicloader.middleware.TemplateSwitcherMiddleware',
	'maintenance.middleware.MaintenanceMiddleware',
)

AUTHENTICATION_BACKENDS = (
	'django.contrib.auth.backends.ModelBackend',
	'auth_remember.backend.AuthRememberBackend',
)

ROOT_URLCONF = 'shakal.urls'

WSGI_APPLICATION = 'shakal.wsgi.application'

TEMPLATE_DIRS = (
	os.path.join(ROOT, 'templates'),
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admin',
	'django.contrib.comments',
	'django_tools',
	'antispam',
	'attachment',
	'auth_remember',
	'autoimagefield',
	'bootstrap_toolkit',
	'breadcrumbs',
	'hitcount',
	'html_editor',
	'maintenance',
	'mptt',
	'registration',
	'template_preprocessor',
	'paginator',
	'shakal.accounts',
	'shakal.article',
	'shakal.forum',
	'shakal.linuxos',
	'shakal.news',
	'shakal.survey',
	'shakal.template_dynamicloader',
	'shakal.threaded_comments',
)

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'filters': {
		'require_debug_false': {
			'()': 'django.utils.log.RequireDebugFalse'
		}
	},
	'handlers': {
		'mail_admins': {
			'level': 'ERROR',
			'filters': ['require_debug_false'],
			'class': 'django.utils.log.AdminEmailHandler'
		}
	},
	'loggers': {
		'django.request': {
			'handlers': ['mail_admins'],
			'level': 'ERROR',
			'propagate': True,
		},
	}
}

AUTH_PROFILE_MODULE = 'accounts.UserProfile'

ACCOUNT_ACTIVATION_DAYS = 7

ABSOLUTE_URL_OVERRIDES = {
	'auth.user': lambda o: '/profil/{0}/'.format(o.pk)
}

ATTACHMENT_MAX_SIZE = 1024**2 * 50;
ATTACHMENT_SIZE_FOR_CONTENT = {
	'threaded_comments_threadedcomment': 1024**2 * 2
}
