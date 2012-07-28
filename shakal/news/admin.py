# -*- coding: utf-8 -*-

from django.contrib import admin
from shakal.news.models import News

class NewsAdmin(admin.ModelAdmin):
	list_display = ('subject', 'time', 'author', 'approved', )
	list_filter = ('approved', )
	search_fields = ('subject', )
	ordering = ('-id', )
	raw_id_fields = ('author', )

admin.site.register(News, NewsAdmin)
