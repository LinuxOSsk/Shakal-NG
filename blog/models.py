# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q, Case, When
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django_autoslugfield.fields import AutoSlugField

from attachment.models import Attachment
from comments.models import RootHeader, Comment
from common_utils.models import TimestampModelMixin
from hitcount.models import HitCountField
from polls.models import Poll
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


@python_2_unicode_compatible
class Blog(TimestampModelMixin, models.Model):
	author = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	title = models.CharField(max_length=100, verbose_name='názov blogu')
	slug = AutoSlugField(title_field='title', unique=True)
	original_description = RichTextOriginalField(filtered_field='filtered_description', property_name='description', verbose_name='popis blogu', max_length=1000, blank=True)
	filtered_description = RichTextFilteredField()
	original_sidebar = RichTextOriginalField(filtered_field='filtered_sidebar', property_name='sidebar', verbose_name='bočný panel', max_length=1000, blank=True)
	filtered_sidebar = RichTextFilteredField()

	content_fields = ('original_descriptoin', 'original_sidebar',)

	def get_absolute_url(self):
		return reverse('blog:post-list-category', args=(self.slug))

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = 'blog'
		verbose_name_plural = 'blogy'


class PostQuerySet(QuerySet):
	def published(self):
		return self.filter(pub_time__lt=timezone.now())

	def for_auth_user(self, user):
		return self.filter(Q(pub_time__lt=timezone.now()) | Q(blog__author=user))


class PostManager(models.Manager):
	def get_queryset(self):
		return (PostQuerySet(self.model, using=self._db)
			.select_related('blog', 'blog__author')
			.annotate(
				is_published=Case(
					When(pub_time__lte=timezone.now(), then=True),
					default=False,
					output_field=models.BooleanField()
				)
			))

	def published(self):
		return self.get_queryset().published()

	def for_auth_user(self, user):
		return self.get_queryset().for_auth_user(user)


class PublishedPostManager(PostManager):
	def get_queryset(self):
		return super(PublishedPostManager, self).get_queryset().filter(is_published=True)


@python_2_unicode_compatible
class Post(TimestampModelMixin, models.Model):
	all_objects = PostManager()
	objects = PublishedPostManager()

	blog = models.ForeignKey(Blog, on_delete=models.PROTECT)
	title = models.CharField(max_length=100, verbose_name='názov')
	slug = AutoSlugField(title_field='title', in_respect_to=('blog',))
	original_perex = RichTextOriginalField(filtered_field='filtered_perex', property_name='perex', verbose_name='perex', max_length=1000)
	filtered_perex = RichTextFilteredField()
	original_content = RichTextOriginalField(filtered_field='filtered_content', property_name='content', verbose_name='obsah', parsers={'html': 'blog'}, max_length=100000)
	filtered_content = RichTextFilteredField()
	pub_time = models.DateTimeField(verbose_name='čas publikácie', db_index=True)
	linux = models.BooleanField('linuxový blog', default=False)
	polls = GenericRelation(Poll)
	comments_header = GenericRelation(RootHeader)
	comments = GenericRelation(Comment)
	attachments = GenericRelation(Attachment)
	hit = HitCountField()

	content_fields = ('original_perex', 'original_content',)

	def get_absolute_url(self):
		return reverse('blog:post-detail', args=(self.blog.slug, self.slug))

	def published(self):
		if not self.pub_time:
			return False
		return self.pub_time < timezone.now()
	published.short_description = 'je publikovaný'
	published.boolean = True

	@property
	def author(self):
		return self.blog.author

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = 'zápis'
		verbose_name_plural = 'zápisy'
		unique_together = (('blog', 'slug'),)
		ordering = ('-pub_time',)
