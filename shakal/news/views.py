# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.template import RequestContext
from forms import NewsForm
from models import News
from shakal.utils.generic import AddLoggedFormArgumentMixin, PreviewCreateView
from shakal.utils import unique_slugify

def news_detail_by_slug(request, slug):
	news = get_object_or_404(News.objects.select_related('author'), slug = slug)
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
		unique_slugify(news, title_field = 'title')
		if self.request.user.is_authenticated():
			if self.request.user.get_full_name():
				news.authors_name = self.request.user.get_full_name()
			else:
				news.authors_name = self.request.user.username
			news.author = self.request.user
		if self.request.user.has_perm('news.can_change'):
			news.approved = True;
		return super(NewsCreateView, self).form_valid(form)


def news_list(request, page = 1):
	context = {
		'news': News.news.all(),
		'pagenum': page,
	}
	return TemplateResponse(request, "news/news_list.html", RequestContext(request, context))
