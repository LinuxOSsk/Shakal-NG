# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.utils import timezone
from autoslugfield.fields import AutoSlugField
from attachment.models import Attachment
from hitcount.models import HitCountField
from polls.models import Poll
from threaded_comments.models import RootHeader, Comment
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField
from rich_editor import get_parser


class Blog(models.Model):
	author = models.OneToOneField(settings.AUTH_USER_MODEL)
	title = models.CharField(max_length = 100, verbose_name = _('title'))
	slug = AutoSlugField(title_field = "title", unique = True)
	original_description = RichTextOriginalField(filtered_field = "filtered_description", property_name = "description", verbose_name = _('description'), max_length = 1000)
	filtered_description = RichTextFilteredField()
	original_sidebar = RichTextOriginalField(filtered_field = "filtered_sidebar", property_name = "sidebar", verbose_name = _('sidebar'), max_length = 1000)
	filtered_sidebar = RichTextFilteredField()

	@models.permalink
	def get_absolute_url(self):
		return ("blog:view", [self.slug], {})

	def __unicode__(self):
		return self.title


class PostManager(models.Manager):
	def get_query_set(self):
		return super(PostManager, self).get_query_set().select_related("blog", "blog__author")


class PublishedPostManager(PostManager):
	def get_query_set(self):
		return super(PublishedPostManager, self).get_query_set().filter(pub_time__lt = timezone.now())


class Post(models.Model):
	all_objects = PostManager()
	objects = PublishedPostManager()

	blog = models.ForeignKey(Blog)
	title = models.CharField(max_length = 100, verbose_name = _('title'))
	slug = AutoSlugField(title_field = "title", filter_fields = ('blog',))
	original_perex = RichTextOriginalField(filtered_field = "filtered_perex", property_name = "perex", verbose_name = _('perex'), max_length = 1000)
	filtered_perex = RichTextFilteredField()
	original_content = RichTextOriginalField(filtered_field = "filtered_content", property_name = "content", verbose_name = _('content'), parsers = {'html': get_parser('blog')}, max_length = 100000)
	filtered_content = RichTextFilteredField()
	pub_time = models.DateTimeField(verbose_name = _('publication date'), db_index=True)
	updated = models.DateTimeField(editable = False)
	linux = models.BooleanField(_('linux blog'))
	polls = generic.GenericRelation(Poll)
	comments_header = generic.GenericRelation(RootHeader)
	comments = generic.GenericRelation(Comment)
	attachments = generic.GenericRelation(Attachment)
	hit = HitCountField()

	@models.permalink
	def get_absolute_url(self):
		return ("blog:detail", [self.blog.slug, self.slug], {}) #pylint: disable=E1101

	def published(self):
		return self.pub_time < timezone.now()
	published.short_description = _('is published')
	published.boolean = True

	def save(self, *args, **kwargs):
		self.updated = timezone.now()
		return super(Post, self).save(*args, **kwargs)

	def author(self):
		return self.blog.author #pylint: disable=E1101
	author.admin_order_field = 'blog__author'

	def __unicode__(self):
		return self.title

	class Meta:
		unique_together = (('blog', 'slug'),)
