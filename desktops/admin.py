# -*- coding: utf-8 -*-
from django.contrib import admin

from desktops.models import Desktop
from comments.admin import CommentInline


class DesktopAdmin(admin.ModelAdmin):
	list_display = ('title', 'author',)
	raw_id_fields = ('author',)
	inlines = [CommentInline]

	def get_queryset(self, request):
		return super(DesktopAdmin, self).get_queryset(request).select_related('author')


admin.site.register(Desktop, DesktopAdmin)
