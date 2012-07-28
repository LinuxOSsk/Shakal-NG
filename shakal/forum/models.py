# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _

class Section(models.Model):
	name = models.CharField(max_length = 255, verbose_name = _('name'))
	slug = models.SlugField(unique = True)
	description = models.TextField(verbose_name = _('description'))

	def clean(self):
		slug_num = None
		try:
			slug_num = int(self.slug)
		except:
			pass
		if slug_num is not None:
			raise ValidationError(_('Numeric slug values are not allowed'))

	@permalink
	def get_absolute_url(self):
		return ('forum:section', None, {'section': self.slug})

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = _('section')
		verbose_name_plural = _('sections')


class TopicManager(models.Manager):
	def get_query_set(self):
		return super(TopicManager, self).get_query_set().select_related('user', 'section')


class Topic(models.Model):
	objects = TopicManager()

	section = models.ForeignKey(Section)
	subject = models.CharField(max_length = 100, verbose_name = _('subject'))
	text = models.TextField()
	time = models.DateTimeField(auto_now_add = True)
	username = models.CharField(max_length = 50, blank = False, verbose_name = _('user name'))
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

	@permalink
	def get_absolute_url(self):
		return ('forum:topic-detail', None, {'pk': self.pk})

	def __unicode__(self):
		return self.subject

	class Meta:
		verbose_name = _('topic')
		verbose_name_plural = _('topics')
