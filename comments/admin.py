# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ungettext
from mptt.admin import MPTTModelAdmin

from .models import Comment
from .utils import perform_flag, perform_approve, perform_delete
from attachment.admin import AttachmentInline, AttachmentAdminMixin


class CommentAdmin(AttachmentAdminMixin, MPTTModelAdmin):
	fieldsets = (
		(
			None,
			{'fields': ('content_type', 'object_id', 'parent')}
		),
		(
			'Komentár',
			{'fields': ('subject', 'user', 'user_name', 'original_comment')}
		),
		(
			'Metainformácie',
			{'fields': ('ip_address', 'is_public', 'is_removed', 'is_locked')}
		),
	)
	list_display = ('subject', 'name', 'content_type', 'ip_address', 'created', 'is_public', 'is_removed', 'is_locked')
	list_filter = ('created', 'is_public', 'is_removed')
	date_hierarchy = 'created'
	ordering = ('-created',)
	raw_id_fields = ('user', 'parent',)
	search_fields = ('filtered_comment', 'user__username', 'user_name', 'ip_address')
	actions = ['flag_comments', 'approve_comments', 'remove_comments']
	inlines = [AttachmentInline]

	def get_actions(self, request):
		actions = super(CommentAdmin, self).get_actions(request)
		if not request.user.is_superuser:
			actions.pop('delete_selected', None)
		if not request.user.has_perm('comments.can_moderate'):
			actions.pop('approve_comments', None)
			actions.pop('remove_comments', None)

	def flag_comments(self, request, queryset):
		msg = lambda n: ungettext('flagged', 'flagged', n)
		self._flag_comments(request, queryset, perform_flag, msg)
	flag_comments.short_description = 'Označiť zvolené komentáre'

	def approve_comments(self, request, queryset):
		msg = lambda n: ungettext('approved', 'approved', n)
		self._flag_comments(request, queryset, perform_approve, msg)
	approve_comments.short_description = 'Schváliť zvolené komentáre'

	def remove_comments(self, request, queryset):
		msg = lambda n: ungettext('removed', 'removed', n)
		self._flag_comments(request, queryset, perform_delete, msg)
	remove_comments.short_description = 'Odstrániť zvolené komentáre'

	def get_queryset(self, request):
		return super(CommentAdmin, self).get_queryset(request).none()

	def get_model_perms(self, request):
		perms = super(CommentAdmin, self).get_model_perms(request)
		if request.resolver_match.view_name not in ('admin:comments_comment_changelist', 'admin:comments_comment_change', 'admin:comments_comment_delete', 'admin:comments_comment_history', 'admin:comments_comment_add'):
			perms['delete'] = False
			perms['add'] = False
			perms['change'] = False
		return perms

	def _flag_comments(self, request, queryset, action, msg):
		n_comments = 0
		for comment in queryset:
			action(comment)
			n_comments += 1

		msg = ungettext('1 comment was %(action)s.', '%(count)s comments were %(action)s.', n_comments)
		self.message_user(request, msg % {'count': n_comments, 'action': msg(n_comments)})


admin.site.register(Comment, CommentAdmin)
