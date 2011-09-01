# -*- coding: utf-8 -*-

from django.conf import settings

# Nastavenie štandardnej šablóny
TEMPLATE_DEFAULT_SKIN = getattr(settings, 'TEMPLATE_DEFAULT_SKIN', 'default')
TEMPLATE_DEFAULT_DEVICE = getattr(settings, 'TEMPLATE_DEFAULT_DEVICE', 'desktop')
TEMPLATE_STATIC_PATH = getattr(settings, 'TEMPLATE_STATIC_PATH', 'templates')
