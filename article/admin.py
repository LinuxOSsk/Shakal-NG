# -*- coding: utf-8 -*-
from django.contrib import admin
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .admin_forms import ArticleForm
from .models import Category, Article, Series, SeriesArticle
from admin_actions.views import AdminActionsMixin
from attachment.admin import AttachmentInline, AttachmentAdminMixin
from comments.admin import CommentInline


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
	inlines = [AttachmentInline, CommentInline]
	form = ArticleForm
	fieldsets = (
		(None, {'fields': ('title', 'slug', 'category', 'author', 'authors_name', 'pub_time', 'published', 'top', 'image',)}),
		('Obsah', {'fields': ('original_perex', 'original_annotation',)}),
		('Text článku', {'fields': ('original_content',), 'classes': ('full-width',)}),
		(None, {'fields': ('presentation_image',), 'classes': ('full-width',)}),
	)

	def get_queryset(self, request):
		qs = super(ArticleAdmin, self).get_queryset(request)
		return qs.select_related('author')

	def get_changelist_actions(self, obj):
		if not obj:
			return ()
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


class SeriesArticleInline(admin.TabularInline):
	model = SeriesArticle
	raw_id_fields = ('article',)


class SeriesAdmin(admin.ModelAdmin):
	list_display = ('name', 'updated',)
	search_fields = ('name',)
	prepopulated_fields = {'slug': ('name',)}
	inlines = [SeriesArticleInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Series, SeriesAdmin)
