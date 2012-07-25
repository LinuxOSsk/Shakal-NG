# -*- coding: utf-8 -*-

from django.contrib import admin
from shakal.article.models import Category, Article

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', )
	search_fields = ('name', 'slug', )
	prepopulated_fields = {'slug': ('name', )}

class ArticleAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'time', 'published', )
	search_fields = ('title', 'slug', )
	prepopulated_fields = {'slug': ('title', )}
	raw_id_fields = ('author', )
	exclude = ('display_count', )
	list_filter = ('published', 'top', 'category', )
	ordering = ('-id', )

	def queryset(self, request):
		qs = super(ArticleAdmin, self).queryset(request)
		return qs.select_related('author')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
