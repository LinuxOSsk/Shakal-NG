# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _, ungettext
from mptt.admin import MPTTModelAdmin

from attachment.admin import AttachmentInline
from threaded_comments.models import Comment
from views import perform_flag, perform_approve, perform_delete


class CommentAdmin(MPTTModelAdmin):
	fieldsets = (
		(
			None,
			{'fields': ('content_type', 'object_id')}
		),
		(
			_('Content'),
			{'fields': ('subject', 'user', 'user_name', 'original_comment')}
		),
		(
			_('Metadata'),
			{'fields': ('submit_date', 'ip_address', 'is_public', 'is_removed', 'is_locked')}
		),
	)
	list_display = ('subject', 'name', 'content_type', 'ip_address', 'submit_date', 'is_public', 'is_removed', 'is_locked')
	list_filter = ('submit_date', 'is_public', 'is_removed')
	date_hierarchy = 'submit_date'
	ordering = ('-submit_date',)
	raw_id_fields = ('user',)
	search_fields = ('filtered_comment', 'user__username', 'user_name', 'ip_address')
	actions = ["flag_comments", "approve_comments", "remove_comments"]
	inlines = [AttachmentInline]

	def get_actions(self, request):
		actions = super(CommentAdmin, self).get_actions(request)
		if not request.user.is_superuser:
			actions.pop("delete_selected", None)
		if not request.user.has_perm('comments.can_moderate'):
			actions.pop("approve_comments", None)
			actions.pop("remove_comments", None)

	def flag_comments(self, request, queryset):
		msg = lambda n: ungettext('flagged', 'flagged', n)
		self._flag_comments(request, queryset, perform_flag, msg)
	flag_comments.short_description = _("Flag selected comments")

	def approve_comments(self, request, queryset):
		msg = lambda n: ungettext('approved', 'approved', n)
		self._flag_comments(request, queryset, perform_approve, msg)
	approve_comments.short_description = _("Approve selected comments")

	def remove_comments(self, request, queryset):
		msg = lambda n: ungettext('removed', 'removed', n)
		self._flag_comments(request, queryset, perform_delete, msg)
	remove_comments.short_description = _("Remove selected comments")

	def _flag_comments(self, request, queryset, action, msg):
		n_comments = 0
		for comment in queryset:
			action(comment)
			n_comments += 1

		msg = ungettext('1 comment was %(action)s.', '%(count)s comments were %(action)s.', n_comments)
		self.message_user(request, msg % {'count': n_comments, 'action': msg(n_comments)})


admin.site.register(Comment, CommentAdmin)
