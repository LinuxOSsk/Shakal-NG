# -*- coding: utf-8 -*-
from django.contrib import admin

from polls.forms import PollForm
from polls.models import Choice, Poll


class ChoiceInline(admin.TabularInline):
	model = Choice
	readonly_fields = ('votes', )


class PollAdmin(admin.ModelAdmin):
	form = PollForm
	list_display = ('question', 'approved', )
	search_fields = ('question', 'slug', )
	prepopulated_fields = {'slug': ('question', )}
	list_filter = ('approved', 'content_type', )
	ordering = ('-id', )
	inlines = [ChoiceInline, ]
	exclude = ('choice_count', )


admin.site.register(Poll, PollAdmin)
