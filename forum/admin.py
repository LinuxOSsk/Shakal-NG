# -*- coding: utf-8 -*-
from django.contrib import admin

from attachment.admin import AttachmentInline
from forum.models import Section, Topic


class SectionAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', )
	search_fields = ('name', 'slug', )
	prepopulated_fields = {'slug': ('name', )}


class TopicAdmin(admin.ModelAdmin):
	list_display = ('title', 'get_authors_name', 'is_removed', 'is_resolved', )
	list_filter = ('section', 'is_removed', 'is_resolved', )
	search_fields = ('title', 'get_authors_name', )
	exclude = ('filtered_text', )
	ordering = ('-id', )
	raw_id_fields = ('author', )
	inlines = [AttachmentInline]

admin.site.register(Section, SectionAdmin)
admin.site.register(Topic, TopicAdmin)
