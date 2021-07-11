# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q, Case, When
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils import timezone
from django_autoslugfield.fields import AutoSlugField
from autoimagefield.fields import AutoImageField

from common_utils.models import TimestampModelMixin
from hitcount.models import HitCountField
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


class Blog(TimestampModelMixin, models.Model):
	author = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		verbose_name="autor",
		on_delete=models.CASCADE
	)
	title = models.CharField(
		verbose_name="názov blogu",
		max_length=100
	)
	slug = AutoSlugField(
		verbose_name="skratka URL",
		title_field='title',
		unique=True
	)
	original_description = RichTextOriginalField(
		verbose_name="popis blogu",
		filtered_field='filtered_description',
		property_name='description',
		max_length=1000,
		blank=True
	)
	filtered_description = RichTextFilteredField(
	)
	original_sidebar = RichTextOriginalField(
		verbose_name="bočný panel",
		filtered_field='filtered_sidebar',
		property_name='sidebar',
		max_length=1000,
		blank=True
	)
	filtered_sidebar = RichTextFilteredField(
	)
	image = AutoImageField(
		verbose_name="obrázok",
		upload_to='blog/info/images',
		blank=True
	)

	content_fields = ('original_descriptoin', 'original_sidebar',)
	rating_statistics = GenericRelation('rating.Statistics')
	notification_events = GenericRelation('notifications.Event')

	def get_absolute_url(self):
		return reverse('blog:post-list-category', kwargs={'category': self.slug, 'page': 1})

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = "blog"
		verbose_name_plural = "blogy"


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


class Post(TimestampModelMixin, models.Model):
	all_objects = PostManager()
	objects = PublishedPostManager()

	blog = models.ForeignKey(
		Blog,
		verbose_name="blog",
		on_delete=models.PROTECT
	)
	title = models.CharField(
		verbose_name="názov",
		max_length=100
	)
	slug = AutoSlugField(
		verbose_name="skratka URL",
		title_field='title',
		in_respect_to=('blog',)
	)
	original_perex = RichTextOriginalField(
		verbose_name="perex",
		filtered_field='filtered_perex',
		property_name='perex',
		max_length=1000
	)
	filtered_perex = RichTextFilteredField(
	)
	original_content = RichTextOriginalField(
		verbose_name="obsah",
		filtered_field='filtered_content',
		property_name='content',
		parsers={'html': 'blog'},
		max_length=100000
	)
	filtered_content = RichTextFilteredField(
	)
	pub_time = models.DateTimeField(
		verbose_name="čas publikácie",
		db_index=True
	)
	linux = models.BooleanField(
		"linuxový blog",
		default=False
	)
	image = AutoImageField(
		verbose_name="obrázok",
		upload_to='blog/title/images',
		blank=True
	)

	polls = GenericRelation('polls.Poll')
	comments_header = GenericRelation('comments.RootHeader')
	comments = GenericRelation('comments.Comment')
	attachments = GenericRelation('attachment.Attachment')
	rating_statistics = GenericRelation('rating.Statistics')
	notification_events = GenericRelation('notifications.Event')
	hit = HitCountField()

	content_fields = ('original_perex', 'original_content',)

	def get_absolute_url(self):
		return reverse('blog:post-detail', args=(self.blog.slug, self.slug))

	def published(self):
		if not self.pub_time:
			return False
		return self.pub_time < timezone.now()
	published.short_description = "je publikovaný"
	published.boolean = True

	@property
	def author(self):
		return self.blog.author

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = "zápis"
		verbose_name_plural = "zápisy"
		unique_together = (('blog', 'slug'),)
		ordering = ('-pub_time',)
