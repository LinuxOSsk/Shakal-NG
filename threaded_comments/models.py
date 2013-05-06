# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count, Max
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from attachment.models import Attachment
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class HideRootQuerySet(models.query.QuerySet):
	def __init__(self, *args, **kwargs):
		super(HideRootQuerySet, self).__init__(*args, **kwargs)
		self.__root_item = None
		self.__cache = None

	def has_root_item(self):
		return self.get_root_item() is not None

	def get_root_item(self):
		self.__load_cache_and_root_item()
		return self.__root_item

	def iterator(self):
		self.__load_cache_and_root_item()
		for item in self.__cache:
			if not self.__is_root(item):
				yield item

	def __load_cache_and_root_item(self):
		if self.__cache is not None:
			return
		self.__cache = []
		for item in super(HideRootQuerySet, self).iterator():
			if self.__is_root(item):
				self.__root_item = item
			self.__cache.append(item)

	def __is_root(self, item):
		return item.parent_id is None


class CommentManager(models.Manager):
	use_for_related_fields = True

	def __init__(self, qs_class = models.query.QuerySet):
		self.__qs_class = qs_class
		super(CommentManager, self).__init__()

	def get_root_comment(self, ctype, object_id):
		root_comment, created = self.model.all_comments.get_or_create(
			parent = None,
			content_type = ctype,
			object_id = object_id,
			defaults = {
				'original_comment': ('html', ''),
				'filtered_comment': '',
				'user_name': '',
				'submit_date': timezone.now(),
			}
		)
		return (root_comment, created)

	def get_query_set(self):
		queryset = self.__qs_class(self.model).select_related('user__profile')
		return queryset


class Comment(MPTTModel):
	all_comments = CommentManager()
	objects = CommentManager(HideRootQuerySet)
	plain_objects = models.Manager()

	content_type = models.ForeignKey(ContentType, verbose_name = _('content type'), related_name = "content_type_set_for_%(class)s")
	object_id = models.TextField(_('object ID'))
	content_object = generic.GenericForeignKey("content_type", "object_id")
	parent = TreeForeignKey('self', null = True, blank = True, related_name = 'children')

	subject = models.CharField(max_length = 100)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = _('user'), blank = True, null = True, related_name = "%(class)s_comments")
	user_name = models.CharField(_("user's name"), max_length = 50, blank = True)
	original_comment = RichTextOriginalField()
	filtered_comment = RichTextFilteredField(original_field = "original_comment", property_name = "comment")

	submit_date = models.DateTimeField(_('date/time submitted'), default = None)
	ip_address = models.IPAddressField(_('IP address'), blank = True, null = True)
	is_public = models.BooleanField(_('is public'), default = True)
	is_removed = models.BooleanField(_('is removed'), default = False)

	is_locked = models.BooleanField(_('is locked'), default = False)
	updated = models.DateTimeField(editable = False)
	attachments = generic.GenericRelation(Attachment)

	def root_header(self):
		header, created = RootHeader.objects.get_or_create(content_type = self.content_type, object_id = self.object_id)
		if created:
			header.pub_date = self.submit_date
			header.save()
		return header

	def get_absolute_url(self):
		return reverse('comment', args = [self.pk], kwargs = {}) + "#link_" + str(self.id)

	def _get_name(self):
		return self.user_name
	name = property(_get_name)

	@models.permalink
	def get_single_comment_url(self):
		return ('comment-single', (self.pk,), {})

	def get_tags(self):
		tags = []
		if hasattr(self, 'is_new'):
			if self.is_new:
				tags.append('new')
		if not self.is_public:
			tags.append('private')
		if self.is_removed:
			tags.append('deleted')
		if tags:
			return u' ' + u' '.join(tags)
		else:
			return u''

	def save(self, *args, **kwargs):
		self.updated = timezone.now()
		if not self.id:
			self.submit_date = self.updated
		if self.submit_date is None:
			self.submit_date = timezone.now()
		return super(Comment, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.subject

	class Meta:
		ordering = ('tree_id', 'lft')
		index_together = [['object_id', 'content_type']]
		verbose_name = _('comment')
		verbose_name_plural = _('comments')
		db_table = 'django_comments'


class CommentFlag(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), related_name="threadedcomment_flags")
	comment = models.ForeignKey(Comment, verbose_name=_('comment'), related_name="flags")
	flag = models.CharField(_('flag'), max_length=30, db_index=True)
	flag_date = models.DateTimeField(_('date'), default=None)

	SUGGEST_REMOVAL = "removal suggestion"
	MODERATOR_DELETION = "moderator deletion"
	MODERATOR_APPROVAL = "moderator approval"

	class Meta:
		db_table = 'django_comment_flags'
		unique_together = [('user', 'comment', 'flag')]
		verbose_name = _('comment flag')
		verbose_name_plural = _('comment flags')

	def __unicode__(self):
		return u"%s flag of comment ID %s by %s" % (self.flag, self.comment_id, self.user.get_username())

	def save(self, *args, **kwargs):
		if self.flag_date is None:
			self.flag_date = timezone.now()
		super(CommentFlag, self).save(*args, **kwargs)


class RootHeader(models.Model):
	pub_date = models.DateTimeField(null = False, blank = False, db_index = True)
	last_comment = models.DateTimeField(null = False, blank = False, db_index = True)
	comment_count = models.PositiveIntegerField(default = 0, db_index = True)
	is_locked = models.BooleanField(default = False)
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	@models.permalink
	def get_absolute_url(self):
		return ('comments', [self.pk], {})

	class Meta:
		unique_together = (('content_type', 'object_id'),)
		verbose_name = _('comment')
		verbose_name_plural = _('comments')


def update_comments_header(sender, **kwargs):
	instance = kwargs['instance']
	if instance.parent is None:
		root = instance
	else:
		root = Comment.all_comments.get(content_type = instance.content_type, object_id = instance.object_id, parent = None)
	statistics = Comment.all_comments
	statistics = statistics.filter(content_type = root.content_type, object_id = root.object_id, is_public = True, is_removed = False)
	statistics = statistics.exclude(pk = root.pk)
	statistics = statistics.aggregate(Count('pk'), Max('submit_date'))

	header, created = RootHeader.objects.get_or_create(content_type = root.content_type, object_id = root.object_id, defaults = {'pub_date': root.submit_date})
	header.is_locked = root.is_locked
	header.last_comment = statistics['submit_date__max']
	header.pub_date = root.submit_date
	if header.last_comment is None:
		content_object = root.content_object
		if hasattr(content_object, 'created'):
			header.last_comment = content_object.created
		elif hasattr(content_object, 'time'):
			header.last_comment = content_object.time
	header.comment_count = statistics['pk__count']
	header.save()

post_save.connect(update_comments_header, sender = Comment)


class UserDiscussionAttribute(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	discussion = models.ForeignKey(RootHeader)
	time = models.DateTimeField(null = True, blank = True)
	watch = models.BooleanField(default = False)

	class Meta:
		unique_together = (('user', 'discussion'),)
