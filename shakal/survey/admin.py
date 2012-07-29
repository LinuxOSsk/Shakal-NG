# -*- coding: utf-8 -*-

from django.contrib import admin
from shakal.survey.models import Survey

class SurveyAdmin(admin.ModelAdmin):
	list_display = ('question', 'slug', )
	search_fields = ('question', 'slug', )
	prepopulated_fields = {'slug': ('question', )}
	list_filter = ('approved', 'content_type', )
	ordering = ('-id', )

admin.site.register(Survey, SurveyAdmin)
