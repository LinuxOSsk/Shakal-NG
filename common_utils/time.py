# -*- coding: utf-8 -*-
from django.utils import timezone


def now():
	return timezone.localtime(timezone.now())


def today():
	return now().date()
