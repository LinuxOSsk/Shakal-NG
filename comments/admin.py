# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html, escape, mark_safe
from mptt.admin import DraggableMPTTAdmin

from .models import Comment, RootHeader
from attachment.admin import AttachmentInline, AttachmentAdminMixin


class CommentAdmin(AttachmentAdminMixin, DraggableMPTTAdmin):
	fieldsets = (
		(
			'Komentár',
			{'fields': ('subject', 'user', 'user_name', 'original_comment')}
		),
		(
			'Metainformácie',
			{'fields': ('ip_address', 'is_public', 'is_removed', 'is_locked')}
		),
	)
	list_display = ('tree_actions', 'get_subject', 'name', 'ip_address', 'created', 'is_public', 'is_removed', 'is_locked')
	list_display_links = ('get_subject',)
	list_filter = ('created', 'is_public', 'is_removed',)
	raw_id_fields = ('user',)
	search_fields = ('filtered_comment', 'user__username', 'user_name', 'ip_address')
	inlines = [AttachmentInline]

	def get_subject(self, obj):
		return mark_safe(('<span style="display: inline-block; border-left: 1px solid #ddd; width: 16px; padding-top: 4px; padding-bottom: 8px; margin-top: -4px; margin-bottom: -8px;">&nbsp;</span>' * (obj._mpttfield('level')-1)) + escape(obj.subject))
	get_subject.short_description = 'Predmet'
	get_subject.admin_order_field = 'subject'

	def get_actions(self, request):
		actions = super().get_actions(request)
		if not request.user.is_superuser:
			actions.pop('delete_selected', None)
		return actions

	def get_queryset(self, request):
		qs = super().get_queryset(request).exclude(level=0)
		if 'content_type_id__exact' in request.GET and 'object_id__exact' in request.GET:
			try:
				content_type_id = int(request.GET['content_type_id__exact'])
				object_id = int(request.GET['object_id__exact'])
				return qs.filter(content_type_id=content_type_id, object_id=object_id)
			except ValueError:
				return qs.none()
		if request.resolver_match.view_name in ('admin:comments_comment_change', 'admin:comments_comment_delete', 'admin:comments_comment_history', 'admin:comments_comment_add'):
			return qs
		return qs.none()

	def get_model_perms(self, request):
		perms = super().get_model_perms(request)
		if request.resolver_match.view_name not in ('admin:comments_comment_changelist', 'admin:comments_comment_change', 'admin:comments_comment_delete', 'admin:comments_comment_history', 'admin:comments_comment_add'):
			perms['delete'] = False
			perms['add'] = False
			perms['change'] = False
		return perms


class RootHeaderAdmin(admin.ModelAdmin):
	date_hierarchy = 'pub_date'
	list_display = ('get_name', 'get_link')
	list_display_links = None

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('content_type')

	def has_add_permission(self, request):
		return False

	def get_name(self, obj):
		return format_html('<a href="{}">{}&nbsp;</a>', obj.get_admin_url(), obj.content_object)
	get_name.short_description = "Názov"

	def get_link(self, obj):
		return format_html('<a href="{}">Zobraziť</a>', obj.get_absolute_url())
	get_link.short_description = "Zobraziť"


class CommentInline(GenericTabularInline):
	model = Comment
	fields = ('get_subject',)
	readonly_fields = ('get_subject',)

	template = 'admin/edit_inline/comments.html'

	verbose_name = 'komentár'
	verbose_name_plural = 'komentáre'

	ct_field = 'content_type'
	ct_fk_field = 'object_id'

	extra = 0

	def get_queryset(self, request):
		return super().get_queryset(request).order_by('lft')

	def get_subject(self, obj):
		indent = ''
		if obj.level:
			indent = mark_safe('&nbsp;&nbsp;' * (obj.level-1))
		return format_html("{}{}", indent, obj.subject)
	get_subject.short_description = "Predmet"


admin.site.register(Comment, CommentAdmin)
admin.site.register(RootHeader, RootHeaderAdmin)
