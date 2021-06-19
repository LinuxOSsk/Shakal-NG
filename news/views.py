# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from .forms import NewsForm, NewsChangeForm
from .models import News, Category
from common_utils.generic import PreviewCreateView, PreviewUpdateView, DetailUserProtectedView, ListView
from notes.views import NoteCreateBase
from notifications.models import Event


class NewsListView(ListView):
	queryset = News.objects.all().select_related('category')
	category_model = Category
	paginate_by = 20


class NewsDetailView(DetailUserProtectedView):
	published_field = 'approved'
	author_field = 'author'
	superuser_perm = 'news.change_news'
	queryset = News.all_news.all().select_related('category', 'author')

	def post(self, request, *args, **kwargs):
		news = self.get_object()
		if 'approve' in request.POST and request.user.has_perm('news.change_news'):
			news.approved = request.POST['approve'] == '1'
			news.save()
			Event.objects.deactivate(content_object=news, action_type=Event.CREATE_ACTION)
		return HttpResponseRedirect(news.get_absolute_url())


class NewsCreateView(UserPassesTestMixin, PreviewCreateView):
	model = News
	form_class = NewsForm

	def form_valid(self, form):
		news = form.save(commit=False)

		if self.request.user.has_perm('news.change_news'):
			news.approved = True

		ret = super(NewsCreateView, self).form_valid(form)
		if news.pk and not news.approved:
			messages.add_message(self.request, messages.INFO, "Správa bola uložená, počkajte prosím na schválenie administrátormi.")
			title = "Správa " + news.title + " čaká na schválenie"
			Event.objects.broadcast(
				title,
				news,
				action=Event.CREATE_ACTION,
				author=news.author,
				permissions=(News, 'change_news')
			)
		if news.pk:
			form.move_attachments(news)
		return ret

	def get_success_url(self):
		if self.request.user.is_authenticated:
			return super(NewsCreateView, self).get_success_url()
		else:
			return reverse('home')

	def test_func(self):
		return settings.ANONYMOUS_NEWS or self.request.user.is_authenticated


class NewsUpdateView(LoginRequiredMixin, PreviewUpdateView):
	form_class = NewsChangeForm

	def get_queryset(self):
		if self.request.user.has_perm('news.change_news'):
			return News.all_news.all()
		else:
			return News.all_news.filter(author=self.request.user, approved=False)


class NoteCreate(PermissionRequiredMixin, NoteCreateBase):
	permission_required = 'news.change_news'
	template_name = 'news/note_create.html'

	def get_content_object(self):
		return get_object_or_404(News, slug=self.kwargs['slug'])


class EventListView(NewsListView):
	template_name = 'news/event_list.html'
	queryset = (News.objects.all()
		.select_related('category')
		.filter(event_date__isnull=False)
		.order_by('-event_date', '-pk'))
