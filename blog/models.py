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


class Blog(models.Model):
	author = models.OneToOneField(settings.AUTH_USER_MODEL)
	title = models.CharField(max_length = 255, verbose_name = _('title'))
	slug = AutoSlugField(title_field = "title", unique = True)

	def __unicode__(self):
		return self.title


class Post(models.Model):
	blog = models.ForeignKey(Blog)
	title = models.CharField(max_length = 255, verbose_name = _('title'))
	slug = AutoSlugField(title_field = "title", filter_fields = ('blog',))
	original_perex = RichTextOriginalField(filtered_field = "filtered_perex", property_name = "perex", verbose_name = _('perex'), max_length = 1000)
	filtered_perex = RichTextFilteredField()
	original_content = RichTextOriginalField(filtered_field = "filtered_content", property_name = "content", verbose_name = _('content'), max_length = 100000)
	filtered_content = RichTextFilteredField()
	pub_time = models.DateTimeField(verbose_name = _('publication date'))
	updated = models.DateTimeField(editable = False)
	published = models.BooleanField(default = False, verbose_name = _('is published'))
	linux = models.BooleanField(_('linux blog'))
	polls = generic.GenericRelation(Poll)
	comments_header = generic.GenericRelation(RootHeader)
	comments = generic.GenericRelation(Comment)
	attachments = generic.GenericRelation(Attachment)
	hit = HitCountField()

	def save(self, *args, **kwargs):
		self.updated = timezone.now()
		return super(Post, self).save(*args, **kwargs)

	def author(self):
		return self.blog.author
	author.admin_order_field = 'blog__author'

	def __unicode__(self):
		return self.title

	class Meta:
		unique_together = (('blog', 'slug'),)
