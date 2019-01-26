# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_str
from mptt.models import MPTTModel, TreeForeignKey

from attachment.models import Attachment
from common_utils.models import TimestampModelMixin
from common_utils.url_utils import build_url
from notes.models import Note
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField
from rich_editor.widgets import TextVal


COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 50000)


class CommentManager(models.Manager):
	use_for_related_fields = True

	def get_or_create_root_comment(self, ctype, object_id):
		# pylint: disable=no-member
		try:
			root_comment = self.model.objects.get(parent=None, content_type=ctype, object_id=object_id)
			return (root_comment, False)
		except self.model.DoesNotExist:
			with transaction.atomic():
				root_comment, created = self.model.objects.get_or_create(
					parent=None,
					content_type=ctype,
					object_id=object_id,
					defaults={
						'original_comment': TextVal('html:'),
						'filtered_comment': '',
						'user_name': '',
						'created': timezone.now(),
					}
				)
				return (root_comment, created)


class Comment(MPTTModel, TimestampModelMixin):
	objects = CommentManager()

	content_type = models.ForeignKey(ContentType, verbose_name='typ obsahu', related_name='content_type_set_for_%(class)s', on_delete=models.PROTECT)
	object_id = models.PositiveIntegerField('ID objektu')
	content_object = GenericForeignKey('content_type', 'object_id')
	parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name='nadradený', on_delete=models.CASCADE)

	subject = models.CharField('predmet', max_length=100)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='používateľ', blank=True, null=True, related_name='%(class)s_comments', on_delete=models.SET_NULL)
	user_name = models.CharField('používateľské meno', max_length=50, blank=True)
	original_comment = RichTextOriginalField(filtered_field='filtered_comment', property_name='comment', verbose_name='obsah', max_length=COMMENT_MAX_LENGTH)
	filtered_comment = RichTextFilteredField()

	ip_address = models.GenericIPAddressField('IP adresa', blank=True, null=True)
	is_public = models.BooleanField('verejný', default=True)
	is_removed = models.BooleanField('odstránený', default=False)

	is_locked = models.BooleanField('uzamknutý', default=False)

	attachments = GenericRelation(Attachment)
	notes = GenericRelation(Note)

	content_fields = ('original_comment',)

	def get_or_create_root_header(self):
		try:
			header = RootHeader.objects.get(content_type=self.content_type, object_id=self.object_id)
			return header
		except RootHeader.DoesNotExist:
			with transaction.atomic():
				header, created = RootHeader.objects.get_or_create(content_type=self.content_type, object_id=self.object_id)
				if created:
					header.pub_date = self.created
					header.save()
				return header

	def get_absolute_url(self):
		return '%s#link_%d' % (reverse('comments:comments', args=(self.get_or_create_root_header().pk,), kwargs={}), self.id)

	def get_single_comment_url(self):
		return reverse('comments:comment-single', args=(self.pk,))

	def get_tags(self):
		tags = []
		if getattr(self, 'is_new', False):
			tags.append('new')
		if not self.is_public:
			tags.append('private')
		if self.is_removed:
			tags.append('deleted')
		if tags:
			return ' ' + ' '.join(tags)
		else:
			return ''

	def _get_name(self):
		return self.user_name
	name = property(_get_name)

	def save(self, *args, **kwargs):
		if not self.user_name and self.user:
			self.user_name = force_str(self.user)
		return super().save(*args, **kwargs)

	def __str__(self):
		return self.subject

	class Meta:
		ordering = ('tree_id', 'lft')
		index_together = (('object_id', 'content_type',),)
		verbose_name = 'komentár'
		verbose_name_plural = 'komentáre'


class RootHeader(models.Model):
	pub_date = models.DateTimeField(db_index=True)
	last_comment = models.DateTimeField(db_index=True)
	comment_count = models.PositiveIntegerField(default=0, db_index=True)
	is_locked = models.BooleanField(default=False)
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')

	def __str__(self):
		return '#%d' % self.id

	@property
	def title(self):
		return force_str(self.content_object)

	def get_absolute_url(self):
		return reverse('comments:comments', args=(self.pk,))

	def get_admin_url(self):
		url_query = {
			'content_type_id__exact': self.content_type_id,
			'object_id__exact': self.object_id,
		}
		return build_url('admin:comments_comment_changelist', query=url_query)

	class Meta:
		unique_together = (('content_type', 'object_id',),)
		verbose_name = 'diskusia'
		verbose_name_plural = 'diskusie'
		ordering = ('-pk',)


class UserDiscussionAttribute(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	discussion = models.ForeignKey(RootHeader, on_delete=models.CASCADE)
	time = models.DateTimeField(null=True, blank=True)
	watch = models.BooleanField(default=False)

	def __str__(self):
		return '#%d' % self.id

	class Meta:
		unique_together = (('user', 'discussion'),)
