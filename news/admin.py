# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from attachment.admin import AttachmentInline
from news.models import News, Category


class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', )
	search_fields = ('name', 'slug', )
	prepopulated_fields = {'slug': ('name', )}


class NewsAdmin(admin.ModelAdmin):
	list_display = ('title', 'created', 'category', 'approved', )
	list_filter = ('approved', 'category',)
	search_fields = ('title', 'slug',)
	ordering = ('-id',)
	raw_id_fields = ('author',)
	prepopulated_fields = {'slug': ('title',)}
	inlines = [AttachmentInline]

admin.site.register(Category, CategoryAdmin)
admin.site.register(News, NewsAdmin)
