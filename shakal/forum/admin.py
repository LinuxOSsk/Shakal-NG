# -*- coding: utf-8 -*-

from django.contrib import admin
from shakal.forum.models import Section

class SectionAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', )
	search_fields = ('name', 'slug', )
	prepopulated_fields = {'slug': ('name', )}

admin.site.register(Section, SectionAdmin)
