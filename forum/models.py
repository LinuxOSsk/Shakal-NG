# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

from attachment.models import Attachment
from comments.models import RootHeader, Comment
from common_utils.models import TimestampModelMixin
from notes.models import Note
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


FORUM_TOPIC_MAX_LENGTH = getattr(settings, 'FORUM_TOPIC_MAX_LENGTH', 5000)


@python_2_unicode_compatible
class Section(models.Model):
	name = models.CharField('názov', max_length=255)
	slug = models.SlugField(unique=True)
	description = models.TextField('popis')

	def get_absolute_url(self):
		return reverse('forum:section', kwargs={'category': self.slug, 'page': 1})

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'sekcia'
		verbose_name_plural = 'sekcie'


class TopicManager(models.Manager):
	def get_queryset(self):
		return super(TopicManager, self).get_queryset().select_related('author', 'section')

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


@python_2_unicode_compatible
class Topic(TimestampModelMixin, models.Model):
	objects = TopicManager()
	topics = TopicListManager()

	ip_address = models.GenericIPAddressField('IP adresa', blank=True, null=True)
	section = models.ForeignKey(Section, verbose_name='sekcia', on_delete=models.PROTECT)
	title = models.CharField('predmet', max_length=100)
	original_text = RichTextOriginalField(filtered_field="filtered_text", property_name="text", verbose_name='text', max_length=FORUM_TOPIC_MAX_LENGTH)
	filtered_text = RichTextFilteredField()
	authors_name = models.CharField('meno autora', max_length=50, blank=False)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name='autor', on_delete=models.SET_NULL)
	comments_header = GenericRelation(RootHeader)
	attachments = GenericRelation(Attachment)
	comments = GenericRelation(Comment)
	notes = GenericRelation(Note)
	ratings = GenericRelation('rating.Rating')

	is_removed = models.BooleanField('vymazané', default=False)
	is_resolved = models.BooleanField('vyriešené', default=False)

	breadcrumb_label = 'fórum'

	content_fields = ('original_text',)

	def is_public(self):
		return not self.is_removed

	def get_tags(self):
		tags = []
		if self.is_removed:
			tags.append('deleted')
		if self.is_resolved:
			tags.append('resolved')
		if tags:
			return ' ' + ' '.join(tags)
		else:
			return ''

	def get_attachments(self):
		return self.attachments.all()

	def get_authors_name(self):
		if self.author:
			if self.author.get_full_name():
				return self.author.get_full_name()
			else:
				return self.author.username
		else:
			return self.authors_name
	get_authors_name.short_description = 'meno autora'

	def get_absolute_url(self):
		return reverse('forum:topic-detail', kwargs={'pk': self.pk})

	def get_list_url(self):
		return reverse('forum:overview', kwargs={'page': 1})

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = 'téma vo fóre'
		verbose_name_plural = 'témy vo fóre'
