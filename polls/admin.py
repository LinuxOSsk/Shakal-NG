# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .admin_forms import PollForm
from .models import Choice, Poll


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
	exclude = ('answer_count', )


admin.site.register(Poll, PollAdmin)
