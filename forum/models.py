# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import permalink
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from attachment.models import Attachment
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField
from threaded_comments.models import RootHeader, Comment


class Section(models.Model):
	name = models.CharField('Názov', max_length=255)
	slug = models.SlugField(unique=True)
	description = models.TextField('Popis')

	def clean(self):
		slug_num = None
		try:
			slug_num = int(self.slug)
		except ValueError:
			pass
		if slug_num is not None:
			raise ValidationError('Numerické hodnoty nie sú povolené')

	@permalink
	def get_absolute_url(self):
		return ('forum:section', None, {'category': self.slug})

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = 'sekcia'
		verbose_name_plural = 'sekcie'


class TopicManager(models.Manager):
	def get_queryset(self):
		return super(TopicManager, self).get_queryset().select_related('user', 'section')

	def topics(self):
		return self.get_queryset().filter(is_removed=False)


class TopicListManager(models.Manager):
	def get_queryset(self):
		return super(TopicListManager, self).get_queryset().filter(is_removed=False)

	def newest_topics(self, section=None):
		queryset = self.get_queryset()
		if not section is None:
			queryset = queryset.filter(section=section)
		queryset = queryset.order_by('-pk')
		return queryset

	def newest_comments(self):
		queryset = self.get_queryset()
		queryset = queryset.filter(comments_header__last_comment__gt=timezone.now() - timedelta(30))
		queryset = queryset.order_by("-comments_header__last_comment")
		return queryset

	def no_comments(self):
		queryset = self.get_queryset()
		queryset = queryset.filter(comments_header__comment_count=0)
		queryset = queryset.filter(comments_header__last_comment__gt=timezone.now() - timedelta(60))
		queryset = queryset.order_by("-id")
		return queryset

	def most_commented(self):
		queryset = self.get_queryset()
		queryset = queryset.filter(comments_header__last_comment__gt=timezone.now() - timedelta(30))
		queryset = queryset.order_by("-comments_header__comment_count")
		return queryset


class Topic(models.Model):
	objects = TopicManager()
	topics = TopicListManager()

	section = models.ForeignKey(Section, verbose_name='sekcia')
	title = models.CharField('predmet', max_length=100)
	original_text = RichTextOriginalField(filtered_field="filtered_text", property_name="text", verbose_name='text')
	filtered_text = RichTextFilteredField()
	created = models.DateTimeField('čas')
	updated = models.DateTimeField(editable=False)
	authors_name = models.CharField('meno autora', max_length=50, blank=False)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name='autor')
	comments_header = GenericRelation(RootHeader)
	attachments = GenericRelation(Attachment)
	comments = GenericRelation(Comment)
	is_removed = models.BooleanField(_('deleted'), default=False)
	is_resolved = models.BooleanField(_('resolved'), default=False)

	breadcrumb_label = 'fórum'

	def is_public(self):
		return not self.is_removed

	def get_tags(self):
		tags = []
		if self.is_removed:
			tags.append('deleted')
		if self.is_resolved:
			tags.append('resolved')
		if tags:
			return u' ' + u' '.join(tags)
		else:
			return u''

	def get_attachments(self):
		return self.attachments.all()

	def save(self, *args, **kwargs):
		self.updated = timezone.now()
		if not self.id:
			self.created = self.updated
		return super(Topic, self).save(*args, **kwargs)

	def get_authors_name(self):
		if self.author:
			if self.author.get_full_name():
				return self.author.get_full_name()
			else:
				return self.author.username
		else:
			return self.authors_name
	get_authors_name.short_description = _('user name')

	@permalink
	def get_absolute_url(self):
		return ('forum:topic-detail', None, {'pk': self.pk})

	@permalink
	def get_list_url(self):
		return ('forum:overview', None, None)

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name = 'téma'
		verbose_name_plural = 'témy'
