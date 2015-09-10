# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import RedirectView
from django.views.generic.edit import FormView

from .feeds import PostFeed
from blog.forms import BlogForm, PostForm, BlogAttachmentForm
from blog.models import Blog, Post
from common_utils.generic import ListView, PreviewCreateView, PreviewUpdateView, DetailUserProtectedView
from feeds.register import register_feed


class PostListView(ListView):
	queryset = Post.all_objects
	category_key = "slug"
	category_field = "blog"
	category_context = "blog"
	category_model = Blog
	paginate_by = 20

	def get_queryset(self):
		queryset = super(PostListView, self).get_queryset()
		if self.request.user.is_authenticated():
			return queryset.for_auth_user(self.request.user)
		else:
			return queryset.published()

	def get(self, request, *args, **kwargs):
		if "category" in kwargs:
			register_feed(request, PostFeed(blog_slug=kwargs['category']))
		return super(PostListView, self).get(request, *args, **kwargs)


class BlogCreateView(LoginRequiredMixin, PreviewCreateView):
	model = Blog
	template_name = 'blog/blog_create.html'
	success_url = reverse_lazy('blog:my')
	form_class = BlogForm

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super(BlogCreateView, self).form_valid(form)


class BlogUpdateView(LoginRequiredMixin, PreviewUpdateView):
	model = Blog
	template_name = 'blog/blog_update.html'
	success_url = reverse_lazy('blog:my')
	form_class = BlogForm

	def get_object(self, queryset=None):
		return get_object_or_404(queryset or Blog, author=self.request.user)


class PostDetailView(DetailUserProtectedView):
	queryset = Post.all_objects.all()
	author_field = 'blog__author'

	def get_queryset(self):
		return super(PostDetailView, self).get_queryset().filter(blog__slug=self.kwargs['category'])

	def get_context_data(self, **kwargs):
		ctx = super(PostDetailView, self).get_context_data(**kwargs)
		ctx['attachments'] = self.object.attachments.all().prefetch_related('attachmentimage')
		ctx['attachments_files'] = [a for a in ctx['attachments'] if not hasattr(a, 'attachmentimage')]
		ctx['attachments_images'] = [a for a in ctx['attachments'] if hasattr(a, 'attachmentimage')]
		return ctx


class PostUpdateView(LoginRequiredMixin, PreviewUpdateView):
	queryset = Post.all_objects.all()
	form_class = PostForm

	def get_queryset(self):
		return super(PostUpdateView, self).get_queryset().\
			filter(blog__slug=self.kwargs['category'], blog__author=self.request.user)


class PostAttachmentsUpdateView(LoginRequiredMixin, FormView):
	template_name = 'blog/post_attachments.html'
	form_class = BlogAttachmentForm

	def __init__(self, *args, **kwargs):
		super(PostAttachmentsUpdateView, self).__init__(*args, **kwargs)
		self.object = None

	def dispatch(self, request, *args, **kwargs):
		qs = Post.objects.all().\
			filter(blog__author=self.request.user, blog__slug=self.kwargs['category'])
		self.object = get_object_or_404(qs, slug=self.kwargs['slug'])
		return super(PostAttachmentsUpdateView, self).dispatch(request, *args, **kwargs)

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


class PostCreateView(LoginRequiredMixin, PreviewCreateView):
	form_class = PostForm
	model = Post

	def get_initial(self):
		return {
			'pub_time': timezone.now(),
		}

	def form_valid(self, form):
		form.instance.blog = self.request.user.blog
		return super(PostCreateView, self).form_valid(form)


class MyBlogView(LoginRequiredMixin, RedirectView):
	def get_redirect_url(self):
		return get_object_or_404(Blog, author=self.request.user).get_absolute_url()


class MyBlogCreateOrUpdate(LoginRequiredMixin, RedirectView):
	def get_redirect_url(self):
		if hasattr(self.request.user, 'blog'):
			return reverse('blog:blog-update')
		else:
			return reverse('blog:blog-create')
