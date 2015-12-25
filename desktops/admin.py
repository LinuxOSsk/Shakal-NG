# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from desktops.models import Desktop


class DesktopAdmin(admin.ModelAdmin):
	list_display = ('title', 'author',)
	raw_id_fields = ('author',)

	def get_queryset(self, request):
		return super(DesktopAdmin, self).get_queryset(request).select_related('author')


admin.site.register(Desktop, DesktopAdmin)
