# -*- coding: utf-8 -*-
from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Page
from common_utils.admin import render_tree_depth


class PageAdmin(VersionAdmin, admin.ModelAdmin):
	list_display = ('get_title', 'slug', )
	search_fields = ('title', 'original_text', )
	ordering = ('-id', )
	prepopulated_fields = {'slug': ('title', )}
	raw_id_fields = ('parent', 'last_author',)

	def get_queryset(self, request):
		return super().get_queryset(request).with_tree_fields()

	def get_title(self, obj):
		return f'{render_tree_depth(obj)} {obj.title}'
	get_title.short_description = Page._meta.get_field('title').verbose_name
	get_title.admin_order_field = 'title'


admin.site.register(Page, PageAdmin)
