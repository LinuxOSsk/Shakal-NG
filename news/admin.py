# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from attachment.admin import AttachmentInline
from news.models import News


class NewsAdmin(admin.ModelAdmin):
	list_display = ('title', 'created', 'author', 'approved', )
	list_filter = ('approved', )
	search_fields = ('title', 'slug', )
	ordering = ('-id', )
	raw_id_fields = ('author', )
	prepopulated_fields = {'slug': ('title', )}
	inlines = [AttachmentInline]

admin.site.register(News, NewsAdmin)
