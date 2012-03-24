from django.shortcuts import render_to_response
from django.template import RequestContext

from article.models import Article

def home(request):
	return render_to_response('index.html', RequestContext(request, {'articles': Article.published_articles.all()}))
