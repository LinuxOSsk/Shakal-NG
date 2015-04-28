# -*- coding: utf-8 -*-

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
from django.utils.translation import ugettext_lazy as _
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

from .assets import SPRITES

ASSETS_MANAGER_SPRITES = SPRITES

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
DYNAMIC_TEMPLATES = (('desktop', ('default',),),)

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'), )

MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'media'))
MEDIA_URL = '/media/'

MEDIA_CACHE_DIR = os.path.join(MEDIA_ROOT, 'cache')
MEDIA_CACHE_URL = MEDIA_URL + 'cache/'
TEMPLATE_CACHE_DIR = os.path.join(BASE_DIR, 'templates', 'cache')

STATICSITEMAPS_BASE_DIR_SITEMAP = 'shakal.sitemaps.sitemaps'

STATIC_BASE_DIR = ''
STATIC_URL = '/static/'

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'account_my_profile'
ACCOUNT_FORMS = {
	'login': 'accounts.forms.LoginForm',
	'add_email': 'accounts.forms.AddEmailForm',
	'signup': 'accounts.forms.SignupForm',
}
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_ACTIVATION_DAYS = 7
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

STATICFILES_DIRS = (
	os.path.join(BASE_DIR, 'static'),
)

STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	#'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = 'c)vwu21d)0!pi67*_@xyv3qp!*74w50!7795t*!d9rfdu(%8g$'


MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'common_utils.middlewares.ThreadLocal.ThreadLocalMiddleware',
	'template_dynamicloader.middleware.TemplateSwitcherMiddleware',
	'feeds.middleware.FeedsMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'accounts.middleware.AuthRememberMiddleware',
	'maintenance.middleware.MaintenanceMiddleware',
)

AUTHENTICATION_BACKENDS = (
	'django.contrib.auth.backends.ModelBackend',
	'allauth.account.auth_backends.AuthenticationBackend',
	'accounts.backend.AuthRememberBackend',
)

BASE_DIR_URLCONF = 'shakal.urls'

WSGI_APPLICATION = 'shakal.wsgi.application'

#TEMPLATE_DIRS = (
#	os.path.join(BASE_DIR, 'templates'),
#)

INSTALLED_APPS = (
	'admin_actions',
	'admin_dashboard',
	'suit',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admin',
	'django.contrib.syndication',
	'django.contrib.sitemaps',
	'django_assets_manager',
	'django_jinja',
	'allauth',
	'allauth.account',
	'haystack',
	'queued_search',
	'accounts',
	'article',
	'attachment',
	'blog',
	'breadcrumbs',
	'hitcount',
	'imgcompress',
	'maintenance',
	'mptt',
	'notifications',
	'paginator',
	'polls',
	'rich_editor',
	'reversion',
	'threaded_comments',
	'forum',
	'feeds',
	'linuxos',
	'news',
	'search',
	'template_dynamicloader',
	'wiki',
	'static_sitemaps',
)

QUEUE_BACKEND = 'dummy'

COMMENTS_APP = 'threaded_comments'

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

ABSOLUTE_URL_OVERRIDES = {
	'auth.user': lambda o: '/profil/{0}/'.format(o.pk)
}

ATTACHMENT_MAX_SIZE = 1024 * 1024 * 50
ATTACHMENT_SIZE_FOR_CONTENT = {
	'django_comments': 1024 * 1024 * 2,
	'threaded_comments_comment': 1024 * 1024 * 2,
	'forum_topic': 1024 * 1024 * 2,
	'blog_post': 1024 * 1024 * 8,
}

HAYSTACK_CONNECTIONS = {
	'default': {
		'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
	},
}
HAYSTACK_CUSTOM_HIGHLIGHTER = 'search.utils.XapianHighlighter'
HAYSTACK_SIGNAL_PROCESSOR = 'queued_search.signals.QueuedSignalProcessor'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

GRAVATAR_DEFAULT_SIZE = 200
GRAVATAR_URL_PREFIX = "http://sk.gravatar.com/"

FEED_SIZE = 20

ADMIN_DASHBOARD_APP_GROUPS = (
	(
		_('Content management'), {
			'models': (
				'article.*',
				'news.*',
				'wiki.models.*',
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
				'forum.*',
				'threaded_comments.*',
			),
		}
	),
	(
		_('Applications'), {
			'models': ('*',),
			'module': 'AppList',
			'collapsible': True,
		}
	),
)
ADMIN_DASHBOARD_APP_ICONS = {
	'accounts/user': 'user.png',
	'auth/group': 'group.png',
	'sites/site': 'site.png',
	'article/article': 'article.png',
	'news/news': 'news.png',
	'wiki/page': 'wiki.png',
	'threaded_comments/comment': 'comments.png',
	'forum/topic': 'topic.png',
	'polls/poll': 'poll.png',
	'forum/section': 'section.png',
}
SUIT_CONFIG = {
	'ADMIN_NAME': 'Shakal CMS',
	'HEADER_DATE_FORMAT': 'l, d F Y',
	'HEADER_TIME_FORMAT': 'H:i',
	'SHOW_REQUIRED_ASTERISK': True,
	'CONFIRM_UNSAVED_CHANGES': True,
	'SEARCH_URL': '/administracia/accounts/user/',
	'MENU_OPEN_FIRST_CHILD': True,
	'MENU_ICONS': {
		'sites': 'icon-leaf',
		'auth': 'icon-lock',
	},
	'MENU_EXCLUDE': ('auth_remember',),
	'LIST_PER_PAGE': 50,
	'MENU': (
		{
			'label': u'Ankety',
			'icon': 'icon-tasks',
			'permissions': 'polls.change_poll',
			'models': (
				'polls.poll',
			)
		},
		{
			'label': u'Blogy',
			'icon': 'icon-pencil',
			'permissions': 'blog.change_post',
			'models': (
				'blog.post',
				'blog.blog',
			)
		},
		{
			'label': u'Články',
			'icon': 'icon-font',
			'permissions': 'article.change_article',
			'models': (
				'article.article',
				'article.category',
			)
		},
		{
			'label': u'Fórum',
			'icon': 'icon-list',
			'permissions': 'forum.change_topic',
			'models': (
				'forum.topic',
				'forum.section',
			)
		},
		{
			'label': u'Používatelia',
			'icon': 'icon-lock',
			'permissions': 'accounts.change_user',
			'models': (
				'accounts.user',
				'auth.group',
			)
		},
		{
			'label': u'Správy',
			'icon': 'icon-globe',
			'permissions': 'news.change_news',
			'models': (
				'news.news',
			)
		},
		{
			'label': u'Wiki',
			'icon': 'icon-folder-open',
			'permissions': 'wiki.change_page',
			'models': (
				'wiki.page',
			)
		},
	),
}

CONN_MAX_AGE = 300

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
	},
	'jinja': {
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
	},
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

JINJA2_BYTECODE_CACHE_NAME = "jinja"
JINJA2_BYTECODE_CACHE_ENABLE = True

import re

TEMPLATES = [
	{
		"BACKEND": "template_dynamicloader.backend.Jinja2",
		"APP_DIRS": True,
		'DIRS': [
			os.path.join(BASE_DIR, 'templates'),
		],
		"OPTIONS": {
			"match_extension": None,
			"match_regex": re.compile(r"^(?!(admin/|debug_toolbar/|suit/|profiler/)).*"),
			"newstyle_gettext": True,
			"extensions": [
				"jinja2.ext.do",
				"jinja2.ext.loopcontrols",
				"jinja2.ext.with_",
				"jinja2.ext.i18n",
				"jinja2.ext.autoescape",
				"django_jinja.builtins.extensions.CsrfExtension",
				"django_jinja.builtins.extensions.CacheExtension",
				"django_jinja.builtins.extensions.TimezoneExtension",
				"django_jinja.builtins.extensions.UrlsExtension",
				"django_jinja.builtins.extensions.StaticFilesExtension",
				"django_jinja.builtins.extensions.DjangoFiltersExtension",
			],
			'context_processors': TCP + (
				'django.core.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
				'breadcrumbs.context_processors.breadcrumbs',
				'feeds.context_processors.feeds',
				'template_dynamicloader.context_processors.style',
				'allauth.account.context_processors.account'
			),
			"autoescape": True,
			"auto_reload": False,
			"translation_engine": "django.utils.translation",
		}
	},
	{
		"BACKEND": "django.template.backends.django.DjangoTemplates",
		"APP_DIRS": True,
		"DIRS": [
			os.path.join(BASE_DIR, 'templates'),
		],
		"OPTIONS": {
			'context_processors': TCP + (
				'django.contrib.messages.context_processors.messages',
				'django.core.context_processors.request',
			)
		}
	}
]


from .patch_urls import patch_urls
patch_urls()

import sys
if len(sys.argv) > 1 and sys.argv[1] == 'test':
	DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:', }}
	DYNAMIC_TEMPLATES = (('desktop', ('test',),),)

	LANGUAGE_CODE = 'en'
	LANGUAGES = (('en', 'English'),)
	CAPTCHA_DISABLE = True
	LOGIN_URL = '/accounts/login/'
	LOGIN_REDIRECT_URL = '/accounts/me/'

ROOT_URLCONF = 'shakal.urls'
