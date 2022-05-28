# -*- coding: utf-8 -*-
import os
from collections import namedtuple, defaultdict
from datetime import datetime

from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django_jinja import library
from jinja2 import pass_context
from mptt.templatetags import mptt_tags

from ..models import RootHeader, UserDiscussionAttribute
from accounts.models import UserRating, User
from attachment.models import Attachment
from comments.models import Comment
from comments.utils import get_requested_time
from common_utils import iterify, get_meta
from common_utils.content_types import get_lookups


register = template.Library()


class AttachmentRecord(namedtuple('Attachment', ['attachment', 'size'])):
	@property
	def url(self):
		return settings.MEDIA_URL + self.attachment

	@property
	def basename(self):
		return os.path.basename(self.attachment)


class UserRecord(namedtuple('UserRecord', ['pk', 'avatar', 'email', 'username', 'first_name', 'last_name', 'signature', 'distribution', 'is_active', 'is_staff', 'is_superuser', 'rating_value'])):
	def get_absolute_url(self):
		return reverse('accounts:profile', kwargs={'pk': self.pk})

	def get_full_name(self):
		full_name = ('%s %s' % (self.first_name, self.last_name)).strip()
		return full_name or self.username or self.email

	@cached_property
	def rating(self):
		return UserRating(rating=self.rating_value)

	def __str__(self):
		return self.get_full_name() or self.username


class S(str):
	pass


class CommentRecord(object):
	__slots__ = [
		'pk', 'created', 'updated', 'ip_address', 'parent_id', 'level', 'is_public', 'is_removed', 'is_locked', 'subject', 'comment', 'user_name', 'user_id', 'user_avatar', 'user_email', 'user_username', 'user_first_name', 'user_last_name', 'user_signature', 'user_distribution', 'user_is_active', 'user_is_staff', 'user_is_superuser', 'user_rating',
		# extra
		'ip_address_avatar', 'next_new', 'prev_new', 'is_new', 'attachments', 'user'
	]

	_meta = Comment._meta

	def __init__(self, *args):
		self.is_new = False
		self.user = None
		for attr_name, value in zip(self.__slots__, args):
			setattr(self, attr_name, value)
		if self.user_id:
			self.user_avatar = S(self.user_avatar)
			self.user = UserRecord(
				self.user_id,
				self.user_avatar,
				self.user_email,
				self.user_username,
				self.user_first_name,
				self.user_last_name,
				self.user_signature,
				self.user_distribution,
				self.user_is_active,
				self.user_is_staff,
				self.user_is_superuser,
				self.user_rating or 0,
			)
			self.user_avatar.instance = self.user
			self.user_avatar.field = User._meta.get_field('avatar')
			self.user_avatar.name = str(self.user_avatar)

	def get_tags(self):
		tags = []
		if self.is_new:
			tags.append('new')
		if not self.is_public:
			tags.append('private')
		if self.is_removed:
			tags.append('deleted')
		return ' ' + ' '.join(tags)

	@property
	def attachment_count(self):
		return len(self.attachments)

	def get_single_comment_url(self):
		return reverse('comments:comment-single', args=(self.pk,))


class DiscussionLoader:
	DISCUSSION_QUERY_SET = (Comment.objects
		#.select_related('user__rating')
		.only('pk', 'created', 'updated', 'ip_address', 'parent_id', 'subject', 'filtered_comment', 'level', 'is_public', 'is_removed', 'is_locked', 'user_id', 'user_name', 'user', 'user__id', 'user__is_superuser', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'user__is_staff', 'user__is_active', 'user__signature', 'user__distribution', 'user__year', 'user__avatar', 'user__rating__rating')
		#.prefetch_related('attachments')
		.order_by('lft'))

	def __init__(self):
		self.target = None
		self.context = None

	@cached_property
	def target_ctype(self):
		return ContentType.objects.get_for_model(self.target)

	@cached_property
	def root_header(self):
		object_id = self.target.pk
		ctype = self.target_ctype
		try:
			return RootHeader.objects.get(content_type=ctype, object_id=object_id)
		except RootHeader.DoesNotExist:
			with transaction.atomic():
				header = Comment.objects.get_or_create_root_comment(ctype, object_id)[0].get_or_create_root_header()
			return header

	def get_queryset(self):
		object_id = self.target.pk
		ctype = self.target_ctype
		if not object_id:
			return Comment.objects.none()

		queryset = self.DISCUSSION_QUERY_SET.filter(
			content_type=ctype,
			object_id=object_id,
		)
		try:
			queryset[0]
		except IndexError:
			Comment.objects.get_or_create_root_comment(ctype, object_id)
			queryset = self.DISCUSSION_QUERY_SET.filter(
				content_type=ctype,
				object_id=object_id,
			)

		return queryset

	def get_discussion_attribute(self):
		discussion_attribute = UserDiscussionAttribute.objects.get_or_create(user=self.context['user'], discussion=self.root_header)[0]
		return discussion_attribute

	def highlight_new(self, query_set, discussion_attribute):
		last_display_time = self.get_last_display_time(discussion_attribute)
		root_item = query_set.root_item
		prev_new_item = root_item
		for comment in query_set:
			comment.is_new = comment.created >= last_display_time
			if comment.is_new:
				prev_new_item.next_new = comment.pk
				if prev_new_item != root_item:
					comment.prev_new = prev_new_item.pk
				prev_new_item = comment

	def update_discussion_attribute(self, discussion_attribute):
		request = self.context['request']
		discussion_attribute.time = request.request_time
		discussion_attribute.save(update_fields=['time'])

	def get_last_display_time(self, discussion_attribute):
		request = self.context['request']
		last_display_time = request.request_time
		if discussion_attribute.time:
			last_display_time = discussion_attribute.time
		if 'time' in request.GET:
			try:
				time = int(request.GET['time'])
				last_display_time = datetime.utcfromtimestamp(time).replace(tzinfo=timezone.utc)
			except ValueError:
				pass
		return last_display_time

	def load(self, context, target):
		self.target = target
		self.context = context
		attrib = None
		queryset = self.comments_to_list(self.get_queryset())
		if 'user' in context and context['user'].is_authenticated:
			attrib = self.get_discussion_attribute()
			setattr(queryset, 'root_item', queryset[0])
			self.highlight_new(queryset, attrib)
			self.update_discussion_attribute(attrib)
		else:
			setattr(queryset, 'root_item', queryset[0])
		setattr(queryset, 'root_header', self.root_header)
		if 'user' in context and context['user'].is_authenticated:
			setattr(queryset, 'user_attribute', attrib)
		return queryset

	def comments_to_list(self, queryset):
		class L(list):
			def all(self):
				return self
		attachments = (Attachment.objects
			.filter(object_id__in=queryset.values('pk'), content_type=ContentType.objects.get_for_model(Comment))
			.order_by('pk')
			.values_list('object_id', 'attachment', 'size')
		)
		attachments_by_comment = defaultdict(L)
		for attachment in attachments:
			attachments_by_comment[attachment[0]].append(AttachmentRecord(*attachment[1:]))
		queryset = queryset.values_list('pk', 'created', 'updated', 'ip_address', 'parent_id', 'level', 'is_public', 'is_removed', 'is_locked', 'subject', 'filtered_comment', 'user_name', 'user_id', 'user__avatar', 'user__email', 'user__username', 'user__first_name', 'user__last_name', 'user__signature', 'user__distribution', 'user__is_active', 'user__is_staff', 'user__is_superuser', 'user__rating__rating')
		comments = L([CommentRecord(*row) for row in queryset])
		for comment in comments:
			comment.attachments = attachments_by_comment[comment.pk]
		return comments


def load_user_discussion_attributes(headers, user):
	header_ids = [h['id'] for h in headers]
	user_attributes = UserDiscussionAttribute.objects \
		.filter(user=user, discussion__in=header_ids) \
		.values('discussion_id', 'time', 'watch')
	user_attributes = dict([(a['discussion_id'], a) for a in user_attributes])
	for header in headers:
		header.update(user_attributes.get(header['id'], {}))


def copy_attributes(obj, attributes):
	for name, value in attributes.items():
		setattr(obj, name, value)


@pass_context
@library.global_function
def add_discussion_attributes(context, *models):
	discussion_lookups, content_types = get_lookups(models)
	user = context['user'] if 'user' in context and context['user'].is_authenticated else None

	discussion_lookups = {
		content_type: id_list
		for content_type, id_list in discussion_lookups.items() if id_list
	}

	if not discussion_lookups:
		return ''

	headers_filter = Q()
	for content_type, id_list in discussion_lookups.items():
		headers_filter |= Q(content_type=content_type, object_id__in=id_list)

	headers = (RootHeader.objects
		.filter(headers_filter)
		.values('id', 'object_id', 'content_type_id', 'last_comment', 'comment_count', 'is_locked')
	)
	headers_dict = {(obj['object_id'], obj['content_type_id']): obj for obj in headers}

	if user is not None:
		load_user_discussion_attributes(headers, user)

	for model, content_type in zip(models, content_types):
		for obj in model:
			if not obj:
				continue
			if hasattr(obj, 'last_comment'):
				continue
			header = headers_dict.get((obj.pk, content_type.pk), {})
			cache_data = {
				'last_comment': header.get('last_comment', None),
				'comment_count': header.get('comment_count', 0),
				'is_locked': header.get('is_locked', False),
				'rootheader_id': header.get('id', None),
				'discussion_display_time': header.get('time', None),
				'discusison_watch': None,
				'new_comments': None,
			}
			copy_attributes(obj, cache_data)
			obj.discussion_watch = header.get('watch', None)
			if obj.last_comment and obj.discussion_display_time:
				obj.new_comments = obj.discussion_display_time < obj.last_comment
			else:
				obj.new_comments = None

	return ''


@pass_context
@library.global_function
def add_discussion_attributes_heterogenous(context, *models):
	objects_sorted = {}
	for model in models:
		for instance in iterify(model):
			objects_sorted.setdefault(instance.__class__, [])
			objects_sorted[instance.__class__].append(instance)
	add_discussion_attributes(context, *objects_sorted.values())
	return ''


@library.global_function
def get_comments_for_item(item, display_last=False):
	return mark_safe(render_to_string("comments/comment_count.html", {'item': item, 'display_last': display_last}))


@library.global_function
@pass_context
def get_comments_list(context, target):
	loader = DiscussionLoader()
	return loader.load(context, target)


@library.global_function
@pass_context
def render_comments_toplevel(context, target):
	context = dict(context)
	model_class = target.__class__
	templates = (
		"comments/{0}_{1}_comments_toplevel.html".format(*str(get_meta(model_class)).split('.')),
		"comments/{0}_comments_toplevel.html".format(get_meta(model_class).app_label),
		"comments/comments_toplevel.html",
	)
	context.update({"target": target})
	return mark_safe(render_to_string(templates, context))


library.filter(mptt_tags.tree_info)
register.simple_tag(get_comments_list, takes_context=True)


@library.global_function
def comments_count_image_link(instance):
	ctype = ContentType.objects.get_for_model(instance.__class__)
	return reverse('comments:count-image', args=(ctype.pk, instance.pk), kwargs={})


@register.simple_tag
def admin_comments_url(instance):
	content_type = ContentType.objects.get_for_model(instance)
	object_id = instance.pk
	try:
		header = RootHeader.objects.get(content_type=content_type, object_id=object_id)
		return header.get_admin_url()
	except RootHeader.DoesNotExist:
		pass
	return None


@library.global_function
@pass_context
def request_timestamp(context):
	return get_requested_time(context['request'], as_timestamp=True)


@library.filter
def comments_tree_info(items, start_level=-1):
	current_item = None
	prev_level = start_level
	level = start_level
	next_level = start_level
	for item in items:
		prev_level = level
		level = next_level
		next_level = item.level
		if current_item is not None:
			info = {
				'new_level': list(range(prev_level + 1, level + 1)),
				'closed_levels': list(range(level, next_level, -1)),
				'level': level,
			}
			yield current_item, info
		current_item = item
	prev_level = level
	level = next_level
	next_level = start_level
	if current_item is not None:
		info = {
			'new_level': list(range(prev_level + 1, level + 1)),
			'closed_levels': list(range(level, next_level, -1)),
			'level': level,
		}
		yield current_item, info
