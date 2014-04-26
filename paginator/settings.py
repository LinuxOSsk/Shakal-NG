# -*- coding: utf-8 -*-
from django.conf import settings

PAGINATOR_INSIDE_COUNT = getattr(settings, 'PAGINATOR_INSIDE_COUNT', 10)
PAGINATOR_OUTSIDE_COUNT = getattr(settings, 'PAGINATOR_OUTSIDE_COUNT', 2)
