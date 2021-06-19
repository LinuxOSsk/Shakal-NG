# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

from common_utils.models import TimestampModelMixin
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


class VocabularyNodeType(models.Model):
	name = models.CharField(max_length=32, db_column='type')

	def __str__(self):
		return self.name


class Term(MPTTModel, models.Model):
	parent = TreeForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.PROTECT)
	vocabulary = models.ForeignKey(VocabularyNodeType, db_column='vid', on_delete=models.PROTECT)
	name = models.CharField(max_length=255)
	description = models.TextField()

	def get_absolute_url(self):
		return reverse('blackhole:story_list_term', kwargs={'category': self.pk, 'page': 1})

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "blackhole kategória"
		verbose_name_plural = "blackhole kategórie"
		index_together = [
			['tree_id', 'lft']
		]


class Node(TimestampModelMixin, models.Model):
	node_type = models.CharField(max_length=32)
	title = models.CharField(max_length=128)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
	revision = models.ForeignKey('blackhole.NodeRevision', related_name='revisions', on_delete=models.CASCADE)
	is_published = models.BooleanField(blank=True, default=False)
	is_commentable = models.BooleanField(blank=True, default=True)
	is_promoted = models.BooleanField(blank=True, default=False)
	is_sticky = models.BooleanField(blank=True, default=False)
	terms = models.ManyToManyField('blackhole.Term', blank=True)

	comments_header = GenericRelation('comments.RootHeader', related_query_name='blackhole_node')
	comments = GenericRelation('comments.Comment', related_query_name='blackhole_node')

	class Meta:
		verbose_name = 'blackhole článok'
		verbose_name_plural = 'blackhole články'

	def get_absolute_url(self):
		return reverse('blackhole:story_detail', args=(self.pk,))

	def __str__(self):
		return self.title


class NodeRevision(TimestampModelMixin, models.Model):
	node = models.ForeignKey('blackhole.Node', on_delete=models.CASCADE)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
	title = models.CharField(max_length=128)
	original_body = RichTextOriginalField(
		filtered_field='filtered_body',
		property_name='body',
		parsers={'raw': '', 'html': 'full'}
	)
	filtered_body = RichTextFilteredField()
	log = models.TextField(blank=True)

	def __str__(self):
		return self.title


class File(models.Model):
	node = models.ForeignKey('blackhole.Node', on_delete=models.PROTECT)
	filename = models.CharField(max_length=255)
	filepath = models.FileField(upload_to='blackhole')
	filemime = models.CharField(max_length=255)
	filesize = models.IntegerField()

	def __str__(self):
		return self.filename
