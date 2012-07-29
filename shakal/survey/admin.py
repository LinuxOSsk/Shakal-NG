# -*- coding: utf-8 -*-

from django.contrib import admin
from shakal.survey.models import Answer, Survey

class AnswerInline(admin.TabularInline):
	model = Answer
	readonly_fields = ('votes', )

class SurveyAdmin(admin.ModelAdmin):
	list_display = ('question', 'slug', )
	search_fields = ('question', 'slug', )
	prepopulated_fields = {'slug': ('question', )}
	list_filter = ('approved', 'content_type', )
	ordering = ('-id', )
	inlines = [AnswerInline, ]
	exclude = ('answer_count', )

admin.site.register(Survey, SurveyAdmin)
