# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone


def now():
	return timezone.localtime(timezone.now())


def today():
	return now().date()
