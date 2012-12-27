# -*- coding: utf-8 -*-

from django.http import HttpResponseServerError
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.shortcuts import render_to_response
from article.models import Article, Category as ArticleCategory
from forum.models import Topic as ForumTopic
from haystack.views import SearchView as HaystackSearchView
import sys

def error_500(request):
	template = get_template('500.html')
	type, value, tb = sys.exc_info()
	return HttpResponseServerError(template.render(Context({
		'exception_type': type.__name__,
		'exception_value': value,
		'request': request
	})))


def home(request):
	try:
		top_article = Article.articles.filter(top = True).attributes_for_user(request.user)[0:1][0]
		articles = Article.articles.exclude(pk = top_article.pk).attributes_for_user(request.user)
	except IndexError:
		top_article = None
		articles = Article.articles.all().attributes_for_user(request.user)

	context = {
		'top_article': top_article,
		'articles': articles[:5],
		'article_categories': ArticleCategory.objects.all(),
		'forum_new': ForumTopic.topics.newest_comments().attributes_for_user(request.user)[:20],
		'forum_no_comments': ForumTopic.topics.no_comments().attributes_for_user(request.user)[:5],
		'forum_most_comments': ForumTopic.topics.most_commented().attributes_for_user(request.user)[:5],
	}
	return TemplateResponse(request, "home.html", RequestContext(request, context))


class SearchView(HaystackSearchView):
	def create_response(self):
		context = {
			'query': self.query,
			'form': self.form,
			'suggestion': None,
			'results': self.results,
			'pagenum': self.request.GET.get('page', 1),
		}

		if self.results and hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
			context['suggestion'] = self.form.get_suggestion()

		context.update(self.extra_context())
		return render_to_response(self.template, context, context_instance=self.context_class(self.request))
