# -*- coding: utf-8 -*-
from common_utils.generic import AddLoggedFormArgumentMixin, PreviewCreateView, DetailUserProtectedView, ListView, CreateView, UpdateView
from blog.models import Blog, Post
from blog.forms import BlogForm
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404


class BlogListView(ListView):
	queryset = Post.objects.all()


class BlogCategoryView(BlogListView):
	queryset = Post.objects.all()
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
