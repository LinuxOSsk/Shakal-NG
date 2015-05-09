from settings import *
import site
site.addsitedir('/home/mirec/.virtualenvs/shakal/lib/python2.7/site-packages')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT_URLCONF = 'web.urls_local'

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'shakal',
		'USER': 'postgres',
		'PASSWORD': '',
		'HOST': '127.0.0.1',
		'PORT': '5432',
	},
	'linuxos': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'linuxos',
		'USER': 'mirec',
		'PASSWORD': '',
		'HOST': 'localhost',
		'PORT': '3306',
	}
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# TEMPLATE_LOADERS = (
# 	'template_dynamicloader.loader_filesystem.Loader',
# 	('django.template.loaders.cached.Loader', (
# 		'django.template.loaders.filesystem.Loader',
# 		'django.template.loaders.app_directories.Loader',
# 	)),
# )

# debug toolbar
#INSTALLED_APPS += ('debug_toolbar', 'debug_toolbar_htmltidy', )
#MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware', )
INTERNAL_IPS = ('127.0.0.1', )
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
	'debug_toolbar_htmltidy.panels.HTMLTidyDebugPanel',
)
