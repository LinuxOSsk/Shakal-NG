# -*- coding: utf-8 -*-
from django.contrib import admin
from django.template.loader import render_to_string
from django.db.models import Q, Prefetch, F

from .models import Blog, Post, PostCategory, PostSeries
from attachment.admin import AttachmentInline, AttachmentAdminMixin
from comments.admin import CommentInline


class BlogAdmin(admin.ModelAdmin):
	list_display = ('title', 'author',)
	search_fields = ('title', 'slug', 'author',)
	ordering = ('-id',)
	raw_id_fields = ('author',)
	prepopulated_fields = {'slug': ('title',)}


class PostAdmin(AttachmentAdminMixin, admin.ModelAdmin):
	list_display = ('title', 'author', 'get_status')
	search_fields = ('title', 'slug',)
	ordering = ('-id',)
	raw_id_fields = ('blog', 'category', 'series')
	prepopulated_fields = {'slug': ('title',)}
	inlines = [AttachmentInline, CommentInline]
	date_hierarchy = 'pub_time'

	def get_status(self, obj):
		if obj.published():
			cls = 'success'
			text = 'Publikovaný'
		else:
			cls = 'warning'
			text = 'Čaká na publikovanie'
		ctx = {'cls': cls, 'text': text, 'star': obj.linux}
		return render_to_string('admin/partials/label_star.html', ctx)
	get_status.short_description = 'Stav'
	get_status.allow_tags = True

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		field = super().formfield_for_foreignkey(db_field, request, **kwargs)
		if db_field.name == "category":
			q = Q(blog__isnull=True)
			if request.method == 'POST':
				try:
					blog_id = int(request.POST.get('blog'))
					q |= Q(blog_id=blog_id)
				except ValueError:
					pass
			else:
				post_id = request.resolver_match.kwargs.get('object_id')
				if post_id is not None:
					q |= Q(blog__post=post_id)
			field.queryset = field.queryset.filter(q).order_by(F('blog_id').asc(nulls_last=True), 'pk')
		return field


class PostCategoryAdmin(admin.ModelAdmin):
	list_display = ('title', 'blog',)
	search_fields = ('title', 'slug',)
	ordering = ('-id',)
	raw_id_fields = ('blog',)

	def get_queryset(self, request):
		return super().get_queryset(request).prefetch_related(Prefetch('blog', Blog.objects.only('title')))


class PostSeriesAdmin(admin.ModelAdmin):
	list_display = ('title', 'blog',)
	search_fields = ('title', 'slug',)
	ordering = ('-id',)
	raw_id_fields = ('blog',)

	def get_queryset(self, request):
		return super().get_queryset(request).prefetch_related(Prefetch('blog', Blog.objects.only('title')))


admin.site.register(Blog, BlogAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory, PostCategoryAdmin)
admin.site.register(PostSeries, PostSeriesAdmin)
