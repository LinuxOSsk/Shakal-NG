# -*- coding: utf-8 -*-
from django.contrib import admin

from attachment.admin import AttachmentInline
from blog.models import Blog, Post


class BlogAdmin(admin.ModelAdmin):
	list_display = ('title', 'author',)
	search_fields = ('title', 'slug', 'author', )
	ordering = ('-id',)
	raw_id_fields = ('author',)
	prepopulated_fields = {'slug': ('title', )}


class PostAdmin(admin.ModelAdmin):
	list_display = ('title', 'published', 'author')
	list_filter = ('published', )
	search_fields = ('title', 'slug', )
	ordering = ('-id',)
	raw_id_fields = ('blog', )
	prepopulated_fields = {'slug': ('title', )}
	inlines = [AttachmentInline]

admin.site.register(Blog, BlogAdmin)
admin.site.register(Post, PostAdmin)
