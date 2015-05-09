from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']

DEBUG_PROFILE = False
# django-admin.py runserver 0.0.0.0:8000 --noreload --nothreading
if DEBUG_PROFILE:
	INSTALLED_APPS += ('profiler',)
	MIDDLEWARE_CLASSES += ('profiler.middleware.ProfilerMiddleware', 'profiler.middleware.StatProfMiddleware')

INSTALLED_APPS += ('django_extensions',)

ROOT_URLCONF = 'web.urls_local'

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'shakal',
		'USER': 'postgres',
		'PASSWORD': '',
		'HOST': '127.0.0.1',
		'PORT': '5432',
		'CONN_MAX_AGE': 30,
	},
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'mail.linuxos.sk'
#EMAIL_HOST_PASSWORD = 'hvjcWnie52'
#EMAIL_HOST_USER = 'mireq@linuxos.sk'
#EMAIL_PORT = 25
#EMAIL_SUBJECT_PREFIX = '[LinuxOS.sk]'

STATIC_ROOT = '/var/tmp/shakal/static/'

# debug toolbar
#INSTALLED_APPS += ('debug_toolbar', 'debug_panel', )
#MIDDLEWARE_CLASSES += ('debug_panel.middleware.DebugPanelMiddleware', )
#DEBUG_TOOLBAR_CONFIG = {'INSERT_BEFORE': '</xxx>'}

HAYSTACK_CONNECTIONS = {
	'default': {
		'ENGINE': 'xapian_backend.XapianEngine',
		'PATH': os.path.join(BASE_DIR, 'xapian_index'),
		'INCLUDE_SPELLING': False
	},
}
#HAYSTACK_XAPIAN_LANGUAGE = 'sk'

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

#CACHES = {
#	'default': {
#		'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#		'LOCATION': '127.0.0.1:11211',
#		'KEY_PREFIX': 'linuxos',
#	},
#	'jinja': {
#		#'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#		'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#		'LOCATION': '127.0.0.1:11211',
#		'KEY_PREFIX': 'jinja',
#	},
#}

QUEUE_BACKEND = 'redisd'
QUEUE_REDIS_CONNECTION = '127.0.0.1:6379'
QUEUE_REDIS_DB = '0'

ENCRYPT_KEY = "/home/mirec/Documents/Praca/python/shakal/key/public.pem"

STATICSITEMAPS_PING_GOOGLE = False

#INSTALLED_APPS += ('sugar', )
#MIDDLEWARE_CLASSES += ('sugar.middleware.speedtracer.SpeedTracerMiddleware', )
#WSGI_APPLICATION = 'shakal.wsgi_linesman.application'

JINJA2_BYTECODE_CACHE_ENABLE = False

import sys
if len(sys.argv) > 1 and sys.argv[1] == 'test':
	DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:', }}
	del(SESSION_ENGINE)
	del(CACHES)
	JINJA2_BYTECODE_CACHE_ENABLE = False
