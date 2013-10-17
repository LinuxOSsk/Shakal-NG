# -*- coding: utf-8 -*-
from shakal.settings import *
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'test.db', }}
TEMPLATES = (('desktop', ('test',),),)

LANGUAGE_CODE = 'en'
LANGUAGES = (('en', 'English'),)
