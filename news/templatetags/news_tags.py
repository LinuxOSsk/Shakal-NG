# -*- coding: utf-8 -*-

from django import template
from news.models import News

register = template.Library()

@register.inclusion_tag('news/block_news_list.html', takes_context = True)
def news_frontpage(context):
	return {
		'news': News.objects.all()[:10]
	}
