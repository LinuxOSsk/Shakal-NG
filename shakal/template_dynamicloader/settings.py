# -*- coding: utf-8 -*-

from django.conf import settings

TEMPLATE_DEFAULT_SKIN = getattr(settings, 'TEMPLATE_DEFAULT_SKIN', 'default')
TEMPLATE_DEFAULT_DEVICE = getattr(settings, 'TEMPLATE_DEFAULT_DEVICE', 'desktop')
