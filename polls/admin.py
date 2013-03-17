# -*- coding: utf-8 -*-

from django.contrib import admin
from polls.models import Choice, Poll

class ChoiceInline(admin.TabularInline):
	model = Choice
	readonly_fields = ('votes', )

class PollAdmin(admin.ModelAdmin):
	list_display = ('question', 'slug', )
	search_fields = ('question', 'slug', )
	prepopulated_fields = {'slug': ('question', )}
	list_filter = ('approved', 'content_type', )
	ordering = ('-id', )
	inlines = [ChoiceInline, ]
	exclude = ('choice_count', )

admin.site.register(Poll, PollAdmin)
