# -*- coding: utf-8 -*-

from attachment.admin import AttachmentInline
from django.contrib import admin
from shakal.forum.models import Section, Topic

class SectionAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', )
	search_fields = ('name', 'slug', )
	prepopulated_fields = {'slug': ('name', )}

class TopicAdmin(admin.ModelAdmin):
	list_display = ('subject', 'get_authors_name', )
	list_filter = ('section', )
	search_fields = ('subject', 'get_authors_name', )
	ordering = ('-id', )
	raw_id_fields = ('author', )
	inlines = [AttachmentInline]

admin.site.register(Section, SectionAdmin)
admin.site.register(Topic, TopicAdmin)
