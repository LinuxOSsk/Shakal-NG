# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from blog.forms import BlogForm, PostForm
from blog.models import Blog, Post
from common_utils.generic import DetailUserProtectedView, ListView, CreateView, UpdateView, UpdateProtectedView


class BlogListView(ListView):
	queryset = Post.objects
	category_key = "slug"
	category_field = "blog"
	category_context = "blog"
	category = Blog


class BlogCreateView(CreateView):
	model = Blog
	template_name = 'blog/blog_update.html'
	success_url = reverse_lazy('blog:my')
	form_class = BlogForm

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super(BlogCreateView, self).form_valid(form)


class BlogUpdateView(UpdateView):
	model = Blog
	template_name = 'blog/blog_update.html'
	success_url = reverse_lazy('blog:my')
	form_class = BlogForm


class PostDetailView(DetailUserProtectedView):
	author_field = 'author'
	queryset = Post.all_objects.all()

	def get_queryset(self):
		return super(PostDetailView, self).get_queryset().filter(blog__slug=self.kwargs['category']) #pylint: disable=E1101


class PostUpdateView(UpdateProtectedView):
	author_field = 'blog__author'
	queryset = Post.all_objects.all()
	form_class = PostForm

	def get_queryset(self):
		return super(PostUpdateView, self).get_queryset().filter(blog__slug=self.kwargs['category']) #pylint: disable=E1101


class PostCreateView(CreateView):
	form_class = PostForm
	model = Post

	def form_valid(self, form):
		form.instance.blog = self.request.user.blog
		return super(PostCreateView, self).form_valid(form)


@login_required
def edit(request):
	try:
		blog = request.user.blog
		return BlogUpdateView.as_view()(request, pk = blog.pk)
	except Blog.DoesNotExist:
		return BlogCreateView.as_view()(request)


@login_required
def my_blog(request):
	return HttpResponseRedirect(get_object_or_404(Blog, author=request.user).get_absolute_url())
