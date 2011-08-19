from django import template
from shakal.article.models import Article
register = template.Library()

@register.inclusion_tag('article/list.html')
def newest_articles(count):
	articles = Article.objects.defer('article').filter(published = True).order_by('-pubtime')
	return {'articles': articles[:count]}
