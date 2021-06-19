# -*- coding: utf-8 -*-
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from reversion.admin import VersionAdmin

from .models import Page


class PageAdmin(VersionAdmin, MPTTModelAdmin):
	list_display = ('title', 'slug', )
	search_fields = ('title', 'original_text', )
	ordering = ('-id', )
	prepopulated_fields = {'slug': ('title', )}
	raw_id_fields = ('parent', 'last_author',)

admin.site.register(Page, PageAdmin)
