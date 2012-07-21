# -*- coding: utf-8 -*-

from django.contrib import admin
from shakal.article.models import Category

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', )
	search_fields = ('name', 'slug', )
	prepopulated_fields = {'slug': ('name', )}

admin.site.register(Category, CategoryAdmin)
