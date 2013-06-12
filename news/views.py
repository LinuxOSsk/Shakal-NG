# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.response import TemplateResponse

from common_utils.generic import AddLoggedFormArgumentMixin, PreviewCreateView
from forms import NewsForm
from models import News
from notifications.models import Event


def news_detail_by_slug(request, slug):
	if request.user.has_perm('news.can_change'):
		objects = News.all_news
	else:
		objects = News.objects

	news = get_object_or_404(objects.select_related('author'), slug = slug)
	if request.user.has_perm('news.can_change'):
		if 'approve' in request.GET:
			approved = bool(int(request.GET['approve']))
			news.approved = approved
			news.save()
			Event.objects.deactivate(content_object = news, action_type = Event.CREATE_ACTION)

	context = {
		'news': news
	}
	return TemplateResponse(request, "news/news_detail.html", RequestContext(request, context))


class NewsCreateView(AddLoggedFormArgumentMixin, PreviewCreateView):
	model = News
	template_name = 'news/news_create.html'
	form_class = NewsForm

	def form_valid(self, form):
		news = form.save(commit = False)
		if self.request.user.is_authenticated():
			if self.request.user.get_full_name():
				news.authors_name = self.request.user.get_full_name()
			else:
				news.authors_name = self.request.user.username
			news.author = self.request.user
		if self.request.user.has_perm('news.can_change'):
			news.approved = True

		news.updated = news.created
		ret = super(NewsCreateView, self).form_valid(form)
		if news.pk and not news.approved:
			messages.add_message(self.request, messages.INFO, u"Správa bola uložená, počkajte prosím na schválenie administrátormi.")
			author = None
			if self.request.user.is_authenticated():
				author = self.request.user
			title = u"Správa " + news.title + u" čaká na schválenie"
			Event.objects.broadcast(title, news, action = Event.CREATE_ACTION, author = author, is_staff = True, permissions = (News, 'change_news'))
		return ret

	def get_success_url(self):
		if self.request.user.has_perm('news.can_change'):
			return super(NewsCreateView, self).get_success_url()
		else:
			return reverse('home')


def news_list(request, page = 1):
	context = {
		'news': News.objects.all(),
		'pagenum': page,
	}
	return TemplateResponse(request, "news/news_list.html", RequestContext(request, context))
