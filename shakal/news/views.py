# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.template import RequestContext
from models import News

def news_detail_by_slug(request, slug):
	news = get_object_or_404(News.objects.select_related('author'), slug = slug)
	context = {
		'news': news
	}
	return TemplateResponse(request, "news/news_detail.html", RequestContext(request, context))
