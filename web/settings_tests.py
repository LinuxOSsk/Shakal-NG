# -*- coding: utf-8 -*-
from web.settings import *
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'test.db', }}
TEMPLATES = (('desktop', ('test',),),)

LANGUAGE_CODE = 'en'
LANGUAGES = (('en', 'English'),)
CAPTCHA_DISABLE = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/me/'
