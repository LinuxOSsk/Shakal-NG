# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import TweetForm
from .models import Tweet
from common_utils.generic import PreviewCreateView, PreviewUpdateView, DetailView, ListView


class TweetListView(ListView):
	queryset = Tweet.objects.all().prefetch_related('author').order_by('-pk')
	paginate_by = 20


class TweetDetailView(DetailView):
	def get_queryset(self):
		return Tweet.objects.order_by('-pk').prefetch_related('author')


class TweetCreateView(LoginRequiredMixin, PreviewCreateView):
	model = Tweet
	form_class = TweetForm


class TweetUpdateView(LoginRequiredMixin, PreviewUpdateView):
	model = Tweet
	form_class = TweetForm

	def get_queryset(self):
		return (Tweet.objects.all()
			.filter(author=self.request.user))
