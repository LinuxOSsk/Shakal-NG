from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from shakal.article.models import Article, Category

class ArticleDetailView(DetailView):
	model = Article
	template_object_name = 'article'

def view_category(request, slug, page):
	category = get_object_or_404(Category, slug=slug)
	articles = Article.published_articles.order_by('-pubtime').filter(category = category);
	return render_to_response('article/article_category.html', RequestContext(request, {'category': category, 'articles': articles, 'page': page}));

