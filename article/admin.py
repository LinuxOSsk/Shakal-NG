# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .admin_forms import ArticleForm
from .models import Category, Article
from admin_actions.views import AdminActionsMixin
from attachment.admin import AttachmentInline, AttachmentAdminMixin


class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', )
	search_fields = ('name', 'slug', )
	prepopulated_fields = {'slug': ('name', )}


class ArticleAdmin(AttachmentAdminMixin, AdminActionsMixin, admin.ModelAdmin):
	list_display = ('title', 'author', 'pub_time', 'published', )
	search_fields = ('title', 'slug', )
	prepopulated_fields = {'slug': ('title', )}
	raw_id_fields = ('author', )
	list_filter = ('published', 'top', 'category', )
	ordering = ('-id', )
	inlines = [AttachmentInline]
	form = ArticleForm
	fieldsets = (
		(None, {'fields': ('title', 'slug', 'category', 'author', 'authors_name', 'pub_time', 'top', 'image',)}),
		('Obsah', {'fields': ('perex', 'annotation',)}),
		('Text článku', {'fields': ('content',), 'classes': ('full-width',)}),
	)

	def get_queryset(self, request):
		qs = super(ArticleAdmin, self).get_queryset(request)
		return qs.select_related('author')

	def get_changelist_actions(self, obj):
		if obj.is_published():
			return (('set_unpublished', {'label': _('Unpublish'), 'class': 'btn btn-danger'}),)
		else:
			return (('set_published', {'label': _('Publish'), 'class': 'btn btn-success'}),)

	def set_published(self, request, obj, **kwargs):
		obj.published = True
		if not obj.is_published():
			obj.pub_time = timezone.now()
		obj.save()
		return HttpResponseRedirect(request.path)

	def set_unpublished(self, request, obj, **kwargs):
		obj.published = False
		obj.save()
		return HttpResponseRedirect(request.path)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
