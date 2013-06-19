# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from common_utils.generic import AddLoggedFormArgumentMixin, PreviewCreateView, DetailUserProtectedView, ListView
from forms import NewsForm
from models import News
from notifications.models import Event


class NewsListView(ListView):
	queryset = News.objects.all()


class NewsDetailView(DetailUserProtectedView):
	published_field = 'approved'
	author_field = 'author'
	queryset = News.all_news.all()

	def get(self, request, *args, **kwargs):
		news = self.get_object()
		if 'approve' in request.GET and request.user.has_perm('news.can_change'):
			approved = bool(int(request.GET['approve']))
			news.approved = approved
			news.save()
			Event.objects.deactivate(content_object = news, action_type = Event.CREATE_ACTION)
			return HttpResponseRedirect(news.get_absolute_url())
		return super(NewsDetailView, self).get(request, *args, **kwargs)


class NewsCreateView(AddLoggedFormArgumentMixin, PreviewCreateView):
	model = News
	template_name = 'news/news_create.html'
	form_class = NewsForm

	def form_valid(self, form):
		news = form.save(commit = False)

		if self.request.user.has_perm('news.can_change'):
			news.approved = True

		ret = super(NewsCreateView, self).form_valid(form)
		if news.pk and not news.approved:
			messages.add_message(self.request, messages.INFO, u"Správa bola uložená, počkajte prosím na schválenie administrátormi.")
			title = u"Správa " + news.title + u" čaká na schválenie"
			Event.objects.broadcast(title, news, action = Event.CREATE_ACTION, author = news.author, is_staff = True, permissions = (News, 'change_news'))
		return ret

	def get_success_url(self):
		if self.request.user.has_perm('news.can_change'):
			return super(NewsCreateView, self).get_success_url()
		else:
			return reverse('home')
