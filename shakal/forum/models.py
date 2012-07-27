# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Section(models.Model):
	name = models.CharField(max_length = 255, verbose_name = _('name'))
	slug = models.SlugField(unique = True)
	description = models.TextField(verbose_name = _('description'))

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = _('section')
		verbose_name_plural = _('sections')


class Topic(models.Model):
	title = models.CharField(max_length = 100, verbose_name = _('title'))
	text = models.TextField()
	time = models.DateTimeField()
	username = models.CharField(max_length = 50, verbose_name = _('user name'))
	user = models.ForeignKey(User, blank = True, null = True)

	def get_username(self):
		if self.user:
			if self.user.get_full_name():
				return self.user.get_full_name()
			else:
				return self.user.username
		else:
			return self.username
	get_username.short_description = _('user name')

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name = _('topic')
		verbose_name_plural = _('topics')
