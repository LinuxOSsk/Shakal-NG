# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class NewsletterSubscription(models.Model):
	email = models.EmailField(
		_("email address"),
		primary_key=True
	)
	updated = models.DateTimeField(
		"upravené",
		editable=False
	)

	def save(self, *args, **kwargs):
		self.updated = timezone.now()
		return super().save(*args, **kwargs)

	def __str__(self):
		return self.email

	class Meta:
		verbose_name = _("Newsletter subscription")
		verbose_name_plural = _("Newsletter subscriptions")


class MassEmailExclude(models.Model):
	email = models.EmailField(
		_("email address"),
		primary_key=True
	)

	def __str__(self):
		return self.email

	class Meta:
		verbose_name = _("E-mail exclude")
		verbose_name_plural = _("E-mail excludes")
