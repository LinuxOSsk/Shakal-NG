# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.db import models
from django.template.loader import render_to_string

from .models import Blog, Post
from attachment.admin import AttachmentInline, AttachmentAdminMixin
from comments.admin import CommentInline
from common_utils.admin_widgets import DateTimeInput


class BlogAdmin(admin.ModelAdmin):
	list_display = ('title', 'author',)
	search_fields = ('title', 'slug', 'author',)
	ordering = ('-id',)
	raw_id_fields = ('author',)
	prepopulated_fields = {'slug': ('title',)}


class PostAdmin(AttachmentAdminMixin, admin.ModelAdmin):
	list_display = ('title', 'author', 'get_status')
	search_fields = ('title', 'slug',)
	ordering = ('-id',)
	raw_id_fields = ('blog',)
	prepopulated_fields = {'slug': ('title',)}
	inlines = [AttachmentInline, CommentInline]
	date_hierarchy = 'pub_time'
	formfield_overrides = {
		models.DateTimeField: {'widget': DateTimeInput}
	}

	def get_status(self, obj):
		if obj.published():
			cls = 'success'
			text = 'Publikovaný'
		else:
			cls = 'warning'
			text = 'Čaká na publikovanie'
		ctx = {'cls': cls, 'text': text, 'star': obj.linux}
		return render_to_string('admin/partials/label_star.html', ctx)
	get_status.short_description = 'Stav'
	get_status.allow_tags = True


admin.site.register(Blog, BlogAdmin)
admin.site.register(Post, PostAdmin)
