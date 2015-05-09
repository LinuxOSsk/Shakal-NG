# -*- coding: utf-8 -*-
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'web.settings'

from admin_dashboard.site import AdminSite
from django.contrib import admin
admin.site = AdminSite()

import django.core.handlers.wsgi
from linesman.middleware import make_linesman_middleware
application = django.core.handlers.wsgi.WSGIHandler()
application = make_linesman_middleware(application)
