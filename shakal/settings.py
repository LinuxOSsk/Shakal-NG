# Django settings for shakal project.

import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
from django.utils.translation import ugettext_lazy as _

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
USE_TZ = True

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
	'shakal.feeds.context_processors.feeds',
	'shakal.template_dynamicloader.context_processors.style',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'auth_remember.middleware.AuthRememberMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',
	'shakal.template_dynamicloader.middleware.TemplateSwitcherMiddleware',
	'shakal.feeds.middleware.FeedsMiddleware',
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
	'shakal.shakal_dashboard',
	'admin_tools',
	'admin_tools.theming',
	'admin_tools.menu',
	'admin_tools.dashboard',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.syndication',
	'django.contrib.admin',
	'django_tools',
	'haystack',
	'registration',
	'accounts',
	'antispam',
	'article',
	'attachment',
	'auth_remember',
	'autoimagefield',
	'bootstrap_toolkit',
	'breadcrumbs',
	'hitcount',
	'html_editor',
	'imgcompress',
	'maintenance',
	'mptt',
	'paginator',
	'polls',
	'reversion',
	'template_preprocessor',
	'shakal.feeds',
	'shakal.forum',
	'shakal.linuxos',
	'shakal.news',
	'shakal.search',
	'shakal.template_dynamicloader',
	'shakal.threaded_comments',
	'shakal.wiki',
	'fts',
)

COMMENTS_APP = 'shakal.threaded_comments'

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

AUTH_USER_MODEL = 'accounts.User'

ACCOUNT_ACTIVATION_DAYS = 7

ABSOLUTE_URL_OVERRIDES = {
	'auth.user': lambda o: '/profil/{0}/'.format(o.pk)
}

ATTACHMENT_MAX_SIZE = 1024 * 1024 * 50
ATTACHMENT_SIZE_FOR_CONTENT = {
	'django_comments': 1024 * 1024 * 2,
	'forum_topic': 1024 * 1024 * 2,
}

HAYSTACK_CONNECTIONS = {
	'default': {
		'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
	},
}
HAYSTACK_CUSTOM_HIGHLIGHTER = 'shakal.search.utils.XapianHighlighter'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

GRAVATAR_DEFAULT_SIZE = 200
GRAVATAR_URL_PREFIX = "http://sk.gravatar.com/"

FEED_SIZE = 20

SHAKAL_DASHBOARD_APP_GROUPS = (
	(
		_('Content management'), {
			'models': (
				'article.*',
				'shakal.news.*',
				'shakal.wiki.models.*',
			),
			'exclude': (
				'article.models.Category',
			)
		}
	),
	(
		_('Administration'), {
			'models': (
				'accounts.*',
				'django.contrib.auth.*',
				'django.contrib.sites.*',
				'polls.*',
			),
		}
	),
	(
		_('Forum'), {
			'models': (
				'shakal.forum.*',
				'shakal.threaded_comments.*',
			),
		}
	),
	(
		_('Applications'), {
			'models': ('*',),
			'module': 'AppList',
			'exclude': ('auth_remember.*', 'registration.*', ),
			'collapsible': True,
		}
	),
)
SHAKAL_DASHBOARD_APP_ICONS = {
	'accounts/user': 'user.png',
	'auth/group': 'group.png',
	'sites/site': 'site.png',
	'article/article': 'article.png',
	'news/news': 'news.png',
	'wiki/page': 'wiki.png',
	'threaded_comments/threadedcomment': 'comments.png',
	'forum/topic': 'topic.png',
	'polls/poll': 'poll.png',
	'forum/section': 'section.png',
}
ADMIN_TOOLS_INDEX_DASHBOARD = 'shakal.shakal_dashboard.dashboard.ShakalIndexDashboard'
ADMIN_TOOLS_MENU = 'shakal.shakal_dashboard.menu.ShakalMenu'
ADMIN_TOOLS_THEMING_CSS = 'admin/css/shakal.css'

import sys
if len(sys.argv) > 1 and sys.argv[1] == 'test':
	DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:', }}
	TEMPLATES = (('desktop', ('test',),),)

	LANGUAGE_CODE = 'en'
	LANGUAGES = (('en', 'English'),)
