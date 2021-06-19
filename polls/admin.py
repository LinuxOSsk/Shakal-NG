# -*- coding: utf-8 -*-
from django.contrib import admin

from .admin_forms import PollForm
from .models import Choice, Poll


class ChoiceInline(admin.TabularInline):
	model = Choice
	readonly_fields = ('votes',)


class PollAdmin(admin.ModelAdmin):
	form = PollForm
	list_display = ('question', 'approved',)
	search_fields = ('question', 'slug',)
	prepopulated_fields = {'slug': ('question',)}
	list_filter = ('approved', 'content_type',)
	ordering = ('-id', )
	inlines = [ChoiceInline,]
	exclude = ('answer_count',)
	fieldsets = (
		(None, {'fields': ['question', 'slug', 'active_from', 'checkbox', 'approved']}),
		("Pokročilé", {'fields': ['content_type', 'object_id'], 'classes': ['collapse']}),
	)


admin.site.register(Poll, PollAdmin)
