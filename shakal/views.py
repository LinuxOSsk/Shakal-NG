# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.template.response import TemplateResponse
from article.models import Article

def home(request):
	context = {
		'articles': Article.articles.all()[:5]
	}
	return TemplateResponse(request, "home.html", RequestContext(request, context))
