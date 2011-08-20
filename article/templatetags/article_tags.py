from django import template
from django.template import RequestContext
from shakal.article.models import Article
register = template.Library()

@register.inclusion_tag('article/list.html', takes_context = True)
def newest_articles(context, count):
	articles = Article.objects.defer('article').filter(published = True).order_by('-pubtime')
	return {'articles': articles[:count]}
