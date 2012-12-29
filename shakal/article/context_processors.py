# -*- coding: utf-8 -*-

from shakal.article.models import Category


def categories(request):
	return { 'article_categories': Category.objects.all() }
