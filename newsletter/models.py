# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _


class Newsletter(models.Model):
	email = models.EmailField(
		_("email address"),
		primary_key=True
	)

	def __str__(self):
		return self.email

	class Meta:
		verbose_name = _("Newsletter record")
		verbose_name_plural = _("Newsletter records")
