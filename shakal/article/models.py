# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

class Category(models.Model):
	name = models.CharField(max_length = 255, verbose_name = _('name'))
	icon = models.CharField(max_length = 255, verbose_name = _('icon'))
	slug = models.CharField(max_length = 255)
