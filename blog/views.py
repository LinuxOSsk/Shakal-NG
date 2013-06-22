# -*- coding: utf-8 -*-
from common_utils.generic import AddLoggedFormArgumentMixin, PreviewCreateView, DetailUserProtectedView, ListView
from models import Post


class BlogListView(ListView):
	queryset = Post.objects.all()
