# -*- coding: utf-8 -*-
from django.contrib import admin

from news.models import News


class NewsAdmin(admin.ModelAdmin):
	list_display = ('title', 'created', 'author', 'approved', )
	list_filter = ('approved', )
	search_fields = ('title', 'slug', )
	ordering = ('-id', )
	raw_id_fields = ('author', )
	prepopulated_fields = {'slug': ('title', )}
	exclude = ('filtered_short_text', 'filtered_long_text', )

admin.site.register(News, NewsAdmin)
