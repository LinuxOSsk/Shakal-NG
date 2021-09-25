# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.views.generic import RedirectView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView

from .feeds import PostFeed
from .forms import PostCategoryForm, PostSeriesForm
from .models import PostCategory, PostSeries
from blog.forms import BlogForm, PostForm, BlogAttachmentForm
from blog.models import Blog, Post
from common_utils.generic import ListView, PreviewCreateView, PreviewUpdateView, DetailUserProtectedView, RequestFormViewMixin
from feeds.register import register_feed


class PostListView(ListView):
	paginate_by = 20

	def get_queryset(self):
		queryset = self.filter_by_category(Post.all_objects.all()).prefetch_related('category', 'blog')
		if self.series_object:
			queryset = queryset.order_by('created')
		if self.request.user.is_authenticated:
			return queryset.for_auth_user(self.request.user)
		else:
			return queryset.published()

	def get(self, request, *args, **kwargs):
		response = super().get(request, *args, **kwargs)
		if 'blog' in kwargs:
			register_feed(request, PostFeed(blog_slug=kwargs['blog']))
		return response

	@cached_property
	def blog_object(self):
		if not 'blog' in self.kwargs:
			return None
		return get_object_or_404(Blog, slug=self.kwargs['blog'])

	@cached_property
	def category_object(self):
		if not 'category' in self.kwargs or not self.blog_object:
			return None
		blog = self.blog_object
		if blog:
			query = Q(slug=self.kwargs['category']) & Q(Q(blog=blog) | Q(blog__isnull=True))
		else:
			query = Q(slug=self.kwargs['category']) & Q(blog__isnull=True)
		return get_object_or_404(PostCategory, query)

	@cached_property
	def series_object(self):
		blog = self.blog_object
		if not 'series' in self.kwargs or not blog:
			return None
		return get_object_or_404(PostSeries, blog=blog, slug=self.kwargs['series'])

	def filter_by_category(self, queryset):
		q = Q()
		if self.blog_object:
			q &= Q(blog=self.blog_object)
		if self.category_object:
			q &= Q(category=self.category_object)
		if self.series_object:
			q &= Q(series=self.series_object)
		return queryset.filter(q)

	def get_context_data(self, **kwargs):
		kwargs = super().get_context_data(**kwargs)
		kwargs['category'] = self.category_object
		kwargs['series'] = self.series_object
		kwargs['blog'] = self.blog_object
		if self.blog_object:
			kwargs['categories'] = self.get_categories()
			kwargs['series_list'] = self.get_series()
		return kwargs

	def get_categories(self):
		return (PostCategory.objects
			.filter(post__blog=self.blog_object)
			.order_by('pk')
			.annotate(post_count=Count('post')))

	def get_series(self):
		return (PostSeries.objects
			.filter(post__blog=self.blog_object)
			.order_by('-updated', 'pk')
			.annotate(post_count=Count('post')))[:20]


class BlogUpdateView(LoginRequiredMixin, PreviewUpdateView):
	model = Blog
	template_name = 'blog/blog_form.html'
	success_url = reverse_lazy('blog:my')
	form_class = BlogForm
	context_object_name = 'blog'

	def get_object(self, queryset=None):
		return Blog.objects.all().filter(author=self.request.user).first()

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super(BlogUpdateView, self).form_valid(form)


class PostDetailView(DetailUserProtectedView):
	author_field = 'blog__author'
	published_field = 'is_published'

	def get_queryset(self):
		return Post.all_objects.all().filter(blog__slug=self.kwargs['blog'])

	def get_context_data(self, **kwargs):
		ctx = super(PostDetailView, self).get_context_data(**kwargs)
		ctx['attachments'] = self.object.attachments.all().prefetch_related('attachmentimage')
		attachments = [a for a in ctx['attachments'] if a.is_visible]
		ctx['attachments_files'] = [a for a in attachments if not hasattr(a, 'attachmentimage')]
		ctx['attachments_images'] = [a for a in attachments if hasattr(a, 'attachmentimage')]
		return ctx


class PostUpdateView(LoginRequiredMixin, RequestFormViewMixin, PreviewUpdateView):
	form_class = PostForm

	def get_queryset(self):
		return (Post.all_objects.all()
			.filter(blog__slug=self.kwargs['blog'], blog__author=self.request.user))


class PostAttachmentsUpdateView(LoginRequiredMixin, FormView):
	template_name = 'blog/post_attachments.html'
	form_class = BlogAttachmentForm

	def get_object(self):
		qs = Post.all_objects.all().\
			filter(blog__author=self.request.user, blog__slug=self.kwargs['blog'])
		return get_object_or_404(qs, slug=self.kwargs['slug'])

	@cached_property
	def object(self):
		return self.get_object()

	def get_form_kwargs(self):
		kwargs = super(PostAttachmentsUpdateView, self).get_form_kwargs()
		kwargs['content_object'] = self.object
		return kwargs

	def get_context_data(self, **kwargs):
		ctx = super(PostAttachmentsUpdateView, self).get_context_data(**kwargs)
		ctx['object'] = self.object
		return ctx

	def get_success_url(self):
		return self.request.path


class PostCreateView(LoginRequiredMixin, RequestFormViewMixin, PreviewCreateView):
	form_class = PostForm
	model = Post

	def get_initial(self):
		return {
			'pub_time': timezone.now(),
		}

	def form_valid(self, form):
		if hasattr(self.request.user, 'blog'):
			form.instance.blog = self.request.user.blog
		else:
			if 'create' in self.request.POST:
				blog = Blog()
				blog.author = self.request.user
				blog.title = self.request.user.get_full_name()
				blog.save()
				form.instance.blog = blog
		return super(PostCreateView, self).form_valid(form)


class MyBlogView(LoginRequiredMixin, RedirectView):
	permanent = False

	def get_redirect_url(self):
		return get_object_or_404(Blog, author=self.request.user).get_absolute_url()


class BlogManagementMixin(LoginRequiredMixin):
	@cached_property
	def blog(self):
		return get_object_or_404(Blog, slug=self.kwargs['blog'], author=self.request.user)

	def get_context_data(self, **kwargs):
		kwargs = super().get_context_data(**kwargs)
		kwargs['blog'] = self.blog
		return kwargs


class PostCategoryManagementList(BlogManagementMixin, ListView):
	def get_queryset(self):
		return PostCategory.objects.filter(blog=self.blog).order_by('pk')


class PostCategoryCreateView(BlogManagementMixin, CreateView):
	form_class = PostCategoryForm
	template_name = 'blog/postcategory_form.html'

	def form_valid(self, form):
		form.instance.blog = self.blog
		return super().form_valid(form)

	def get_success_url(self):
		return reverse('blog:post-category-management-list', args=(self.blog.slug,))


class PostCategoryUpdateView(BlogManagementMixin, UpdateView):
	form_class = PostCategoryForm
	template_name = 'blog/postcategory_form.html'

	def get_queryset(self):
		return PostCategory.objects.filter(blog=self.blog)

	def get_success_url(self):
		return reverse('blog:post-category-management-list', args=(self.blog.slug,))


class PostCategoryDeleteView(BlogManagementMixin, DeleteView):
	def get_queryset(self):
		return PostCategory.objects.filter(blog=self.blog).order_by('pk')

	def get_success_url(self):
		return reverse('blog:post-category-management-list', args=(self.blog.slug,))


class PostSeriesManagementList(BlogManagementMixin, ListView):
	def get_queryset(self):
		return PostSeries.objects.filter(blog=self.blog).order_by('-updated', 'pk')


class PostSeriesCreateView(BlogManagementMixin, CreateView):
	form_class = PostSeriesForm
	template_name = 'blog/postseries_form.html'

	def form_valid(self, form):
		form.instance.blog = self.blog
		return super().form_valid(form)

	def get_success_url(self):
		return reverse('blog:post-series-management-list', args=(self.blog.slug,))


class PostSeriesUpdateView(BlogManagementMixin, UpdateView):
	form_class = PostSeriesForm
	template_name = 'blog/postseries_form.html'

	def get_queryset(self):
		return PostSeries.objects.filter(blog=self.blog)

	def get_success_url(self):
		return reverse('blog:post-series-management-list', args=(self.blog.slug,))


class PostSeriesDeleteView(BlogManagementMixin, DeleteView):
	def get_queryset(self):
		return PostSeries.objects.filter(blog=self.blog).order_by('pk')

	def get_success_url(self):
		return reverse('blog:post-series-management-list', args=(self.blog.slug,))
