# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Tweet
from comments.admin import CommentInline


class TweetAdmin(admin.ModelAdmin):
	list_display = ('title', 'created',)
	search_fields = ('title', 'slug',)
	ordering = ('-id',)
	raw_id_fields = ('author',)
	prepopulated_fields = {'slug': ('title',)}
	inlines = [CommentInline]


admin.site.register(Tweet, TweetAdmin)
