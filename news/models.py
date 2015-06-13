# -*- coding: utf-8 -*-
from django_autoslugfield.fields import AutoSlugField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import permalink
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from attachment.models import Attachment
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField
from threaded_comments.models import RootHeader, Comment


class NewsManager(models.Manager):
	def get_queryset(self):
		return super(NewsManager, self).get_queryset().select_related('author')


class NewsListManager(models.Manager):
	def get_queryset(self):
		return super(NewsListManager, self).get_queryset().select_related('author').filter(approved = True).order_by('-pk')


class News(models.Model):
	all_news = NewsManager()
	objects = NewsListManager()

	title = models.CharField(max_length = 255, verbose_name = _('title'))
	slug = AutoSlugField(title_field = "title", unique = True)
	original_short_text = RichTextOriginalField(filtered_field = "filtered_short_text", property_name = "short_text", verbose_name = _('short text'))
	filtered_short_text = RichTextFilteredField()
	original_long_text = RichTextOriginalField(filtered_field = "filtered_long_text", property_name = "long_text", verbose_name = _('long text'))
	filtered_long_text = RichTextFilteredField()
	created = models.DateTimeField(verbose_name = _('time'))
	updated = models.DateTimeField(editable = False)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, blank = True, null = True, verbose_name = _('user'))
	authors_name = models.CharField(max_length = 255, verbose_name = _('authors name'))
	approved = models.BooleanField(default = False, verbose_name = _('approved'))
	comments_header = GenericRelation(RootHeader)
	attachments = GenericRelation(Attachment)
	comments = GenericRelation(Comment)

	class Meta:
		verbose_name = _('news item')
		verbose_name_plural = _('news items')

	def save(self, *args, **kwargs):
		self.updated = timezone.now()
		if not self.id:
			self.created = self.updated
		return super(News, self).save(*args, **kwargs)

	@permalink
	def get_absolute_url(self):
		return ('news:detail-by-slug', None, {'slug': self.slug})

	@permalink
	def get_list_url(self):
		return ('news:list', None, None)

	def __unicode__(self):
		return self.title
