# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Note


class NoteAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'author',)
	raw_id_fields = ('author',)
	search_fields = ('original_text',)

	def get_queryset(self, request):
		return super(NoteAdmin, self).get_queryset(request).select_related('author')


admin.site.register(Note, NoteAdmin)
