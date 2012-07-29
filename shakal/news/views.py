# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.template import RequestContext
from forms import NewsForm
from models import News
from shakal.utils.generic import AddLoggedFormArgumentMixin, PreviewCreateView

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
