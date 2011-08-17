from django.views.generic import DetailView
from article.models import Article

class ArticleDetailView(DetailView):
	model = Article
	template_object_name = 'article'

