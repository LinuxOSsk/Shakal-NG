# -*- coding: utf-8 -*-

from django.contrib import admin
from shakal.forum.models import Section, Topic

class SectionAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', )
	search_fields = ('name', 'slug', )
	prepopulated_fields = {'slug': ('name', )}

class TopicAdmin(admin.ModelAdmin):
	list_display = ('title', 'get_username', )
	search_fields = ('title', 'get_username', )
	ordering = ('-id', )
	raw_id_fields = ('user', )

admin.site.register(Section, SectionAdmin)
admin.site.register(Topic, TopicAdmin)
