# -*- coding: utf-8 -*-
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import re
from pathlib import Path


from .assets import ASSETS, SPRITES

BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_MANAGER_SPRITES = SPRITES
ASSETS_MANAGER_FILES = ASSETS

SECRET_KEY = '*h4+%(b@_+-au@mmh^lp3v=^wkddzp(n63883zzm_i5xdnmb+v'

DEBUG = True

ADMINS = (('Miroslav Bendik', 'mireq@linuxos.sk'),)
MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = 'LinuxOS.sk <web@linuxos.sk>'

ALLOWED_HOSTS = []


INSTALLED_APPS = [
	'template_dynamicloader',
	'common_utils',
	# core
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.sites',
	'django.contrib.sitemaps',
	'django.contrib.staticfiles',
	# vendor
	'blackhole',
	'django_assets_manager',
	'django_ajax_utils',
	'django_autoslugfield',
	'django_geoposition_field',
	'django_sample_generator',
	'django_simple_paginator',
	'django_email_log',
	'allauth',
	'allauth.account',
	'compressor',
	'django_jinja',
	'mptt',
	'hijack',
	'reversion',
	'static_sitemaps',
	'easy_thumbnails',
	'tests',
	# apps
	'accounts',
	'article',
	'attachment',
	'autoimagefield',
	'blog',
	'breadcrumbs',
	'comments',
	'desktops',
	'feeds',
	'forum',
	'fulltext',
	'hitcount',
	'linuxos',
	'news',
	'notes',
	'notifications',
	'polls',
	'rating',
	'tweets',
	'wiki',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	# custom
	'hijack.middleware.HijackUserMiddleware',
	'accounts.middleware.LastViewedMiddleware',
	'accounts.middleware.AuthRememberMiddleware',
	'web.middlewares.ThreadLocalMiddleware',
	'template_dynamicloader.middleware.TemplateSwitchMiddleware',
	'feeds.middleware.FeedsMiddleware',
	'linuxos.middleware.HttpsRedirectMiddleware',
]

ROOT_URLCONF = 'web.urls'

TEMPLATES = [
	{
		"BACKEND": "template_dynamicloader.backend.Jinja2",
		'DIRS': [BASE_DIR / 'templates'],
		"OPTIONS": {
			"match_extension": None,
			"match_regex": re.compile(r"^(?!(admin/|debug_toolbar/|profiler/|search/indexes/|reversion/|sitemap.xml|static_sitemaps/|hijack/|django_extensions/)).*"),
			"newstyle_gettext": True,
			"extensions": [
				"jinja2.ext.do",
				"jinja2.ext.loopcontrols",
				"jinja2.ext.i18n",
				"django_jinja.builtins.extensions.CsrfExtension",
				"django_jinja.builtins.extensions.CacheExtension",
				"django_jinja.builtins.extensions.TimezoneExtension",
				"django_jinja.builtins.extensions.UrlsExtension",
				"django_jinja.builtins.extensions.StaticFilesExtension",
				"django_jinja.builtins.extensions.DjangoFiltersExtension",
				"compressor.contrib.jinja2ext.CompressorExtension",
			],
			"context_processors": [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
				'django.template.context_processors.i18n',
				'breadcrumbs.context_processors.breadcrumbs',
				'template_dynamicloader.context_processors.style',
				'linuxos.context_processors.settings',
			],
			"autoescape": True,
			"auto_reload": True,
			"translation_engine": "django.utils.translation",
			"environment": "template_dynamicloader.environment.Environment",
			"bytecode_cache": {
				"name": "jinja",
				"enabled": True,
			}
		}
	},
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [BASE_DIR / 'templates'],
		'OPTIONS': {
			'loaders': [
				'django.template.loaders.filesystem.Loader',
				'django.template.loaders.app_directories.Loader',
			],
			'context_processors': [
				#'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

DYNAMIC_TEMPLATES = ('alpha', '2013', '386')

AUTH_PASSWORD_VALIDATORS = [
	{ 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
	{ 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
	{ 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
	{ 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
		'KEY_PREFIX': 'linuxos',
		'LOCATION': 'linuxos-default',
	},
	'jinja': {
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
		'KEY_PREFIX': 'jinja',
		'LOCATION': 'linuxos-jinja',
	},
}

WSGI_APPLICATION = os.environ.get('DJANGO_WSGI_APPLICATION', 'web.wsgi.application')

SITE_ID = 1

BASE_URI = 'https://linuxos.sk'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': BASE_DIR / 'db.sqlite3',
	}
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'sk'

LOCALE_PATHS = (BASE_DIR / 'locale',)

LANGUAGES = (('sk', 'Slovak'),)

TIME_ZONE = 'Europe/Bratislava'

USE_I18N = True
USE_TZ = True

SHORT_DATE_FORMAT = 'd. m. Y'
SHORT_DATETIME_FORMAT = 'd. m. Y H:i'

FORM_RENDERER = 'linuxos.form_renderers.Jinja2'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

FEED_SIZE = 20

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATICFILES_DIRS = (BASE_DIR / 'static',)
STATIC_URL = '/static/'
STATICSITEMAPS_URL = 'https://linuxos.sk/static/'
STATICSITEMAPS_MOCK_SITE = True
STATICSITEMAPS_MOCK_SITE_NAME = 'linuxos.sk'
STATICSITEMAPS_MOCK_SITE_PROTOCOL = 'https'
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	'compressor.finders.CompressorFinder',
)
STATIC_ROOT = BASE_DIR.parent / 'static_assets' / 'static'

STATICSITEMAPS_ROOT_SITEMAP = 'web.sitemaps.sitemaps'

MEDIA_ROOT = BASE_DIR.parent / 'static_assets' / 'media'
MEDIA_URL = '/media/'

MEDIA_CACHE_DIR = MEDIA_ROOT / 'cache'
MEDIA_CACHE_URL = MEDIA_URL + 'cache/'

# allauth
LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'accounts:my_profile'
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
ACCOUNT_USERNAME_VALIDATORS = 'accounts.validators.username_validators'

AUTH_USER_MODEL = 'accounts.User'
AUTHENTICATION_BACKENDS = (
	'django.contrib.auth.backends.ModelBackend',
	'accounts.backend.AuthenticationBackend',
	'accounts.backend.AuthRememberBackend',
)

EMAIL_BACKEND = 'django_email_log.backends.EmailBackend'
EMAIL_LOG_BACKEND = 'django.core.mail.backends.console.EmailBackend'

HIJACK_REGISTER_ADMIN = False
HIJACK_ALLOW_GET_REQUESTS = True
HIJACK_LOGIN_REDIRECT_URL = '/profil/ja/'
HIJACK_LOGOUT_REDIRECT_URL = '/administracia/accounts/user/'

INITIAL_DATA_COUNT = {
	'accounts_user': 10,
	'article_article': 20,
	'article_category': 4,
	'blog_post': 30,
	'forum_topic': 30,
	'news_news': 30,
	'tweets_tweet': 30,
}

SAMPLE_DATA_GENERATORS = (
	'accounts.generators',
	'article.generators',
	'blog.generators',
	'forum.generators',
	'news.generators',
	'tweets.generators',
	'comments.generators',
)

ATTACHMENT_MAX_SIZE = 1024 * 1024 * 50
ATTACHMENT_SIZE_FOR_CONTENT = {
	'comments_comment': 1024 * 1024 * 2,
	'forum_topic': 1024 * 1024 * 2,
	'news_news': 1024 * 1024 * 4,
	'blog_post': 1024 * 1024 * 8,
}

HAYSTACK_CONNECTIONS = {
	'default': {
		'ENGINE': 'search.backends.SimpleEngine',
	},
}


GRAVATAR_DEFAULT_SIZE = 200
GRAVATAR_URL_PREFIX = "//sk.gravatar.com/"

QUEUE_BACKEND = 'dummy'

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
			'class': 'django.utils.log.AdminEmailHandler',
			'include_html': True,
		}
	},
	'loggers': {
		'django.request': {
			'handlers': ['mail_admins'],
			'level': 'ERROR',
			'propagate': True,
		},
		'.': {
			'handlers': ['mail_admins'],
			'level': 'ERROR',
			'propagate': True,
		},
	}
}

def COMPRESS_JINJA2_GET_ENVIRONMENT():
	from django.template import engines
	return engines.all()[0].env

COMPRESS_ROOT = BASE_DIR / 'static'
COMPRESS_PRECOMPILERS = (
	('text/x-scss', 'django_libsass.SassCompiler'),
)

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = False
COMPRESS_REBUILD_TIMEOUT = 1
COMPRESS_CSS_HASHING_METHOD = 'content'


#LIBSASS_SOURCE_COMMENTS = False
#LIBSASS_OUTPUT_STYLE = 'compressed'

THUMBNAIL_PRESERVE_EXTENSIONS = True
THUMBNAIL_NAMER = 'autoimagefield.namers.default'
THUMBNAIL_BASEDIR = 'thumbs'
THUMBNAIL_PROCESSORS = (
	'easy_thumbnails.processors.colorspace',
	'easy_thumbnails.processors.autocrop',
	'easy_thumbnails.processors.scale_and_crop',
	'easy_thumbnails.processors.filters',
	'easy_thumbnails.processors.background',
)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

ANONYMOUS_COMMENTS = False
ANONYMOUS_NEWS = True
ANONYMOUS_TOPIC = False
