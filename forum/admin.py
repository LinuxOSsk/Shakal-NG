# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Section, Topic
from attachment.admin import AttachmentInline, AttachmentAdminMixin
from comments.admin import CommentInline


class SectionAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug',)
	search_fields = ('name', 'slug',)
	prepopulated_fields = {'slug': ('name',)}


class TopicAdmin(AttachmentAdminMixin, admin.ModelAdmin):
	list_display = ('title', 'get_authors_name', 'is_removed', 'is_resolved',)
	list_filter = ('section', 'is_removed', 'is_resolved',)
	search_fields = ('title', 'original_text',)
	ordering = ('-id',)
	raw_id_fields = ('author',)
	inlines = [AttachmentInline, CommentInline]


admin.site.register(Section, SectionAdmin)
admin.site.register(Topic, TopicAdmin)
