# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .forms import TweetForm
from .models import Tweet
from common_utils.generic import PreviewCreateView, DetailView, ListView


class TweetListView(ListView):
	queryset = Tweet.objects.all().prefetch_related('author').order_by('-pk')
	paginate_by = 20


class TweetDetailView(DetailView):
	def get_queryset(self):
		return Tweet.objects.order_by('-pk').prefetch_related('author')


class TweetCreateView(PreviewCreateView):
	model = Tweet
	form_class = TweetForm
