# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from common_utils.models import TimestampModelMixin
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


class VocabularyNodeType(models.Model):
	name = models.CharField(max_length=32, db_column='type')

	def __unicode__(self):
		return self.name


class Term(models.Model):
	parent = models.ForeignKey('self')
	vocabulary_type = models.ForeignKey(VocabularyNodeType, db_column='vid')
	name = models.CharField(max_length=255)
	description = models.TextField()

	def __unicode__(self):
		return self.name


class Node(TimestampModelMixin, models.Model):
	vocabulary = models.ForeignKey(VocabularyNodeType)
	title = models.CharField(max_length=128)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	published = models.BooleanField(blank=True, default=False)
	comments_allowed = models.BooleanField(blank=True, default=True)
	is_promoted = models.BooleanField(blank=True, default=False)
	is_sticky = models.BooleanField(blank=True, default=False)

	def __unicode__(self):
		return self.title


class NodeRevision(models.Model):
	node = models.ForeignKey('blackhole.Node')
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	title = models.CharField(max_length=128)
	original_body = RichTextOriginalField(
		filtered_field='filtered_body',
		property_name='body',
		parsers={'raw': '', 'html': 'full'}
	)
	filtered_body = RichTextFilteredField()

	def __unicode__(self):
		return self.title
