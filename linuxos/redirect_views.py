# -*- coding: utf-8 -*-
from django.http.response import HttpResponsePermanentRedirect, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.urls import reverse

from article.models import Article, Category as ArticleCategory
from forum.models import Section as ForumSection
from news.models import News
from polls.models import Poll
from wiki.models import Page as WikiPage


def profile_redirect(request, pk, *args, **kwargs):
	return HttpResponsePermanentRedirect(reverse('accounts:profile', kwargs={'pk': pk}))

def article_redirect(request, pk):
	article = get_object_or_404(Article, pk=pk)
	return HttpResponsePermanentRedirect(reverse('article:detail', kwargs={'slug': article.slug}))

def article_old_redirect(request):
	pk = request.GET.get('clanokid', '')
	try:
		pk = int(pk)
	except ValueError:
		return HttpResponseBadRequest()
	article = get_object_or_404(Article, pk=pk)
	return HttpResponsePermanentRedirect(article.get_absolute_url())

def profile_old_redirect(request):
	pk = request.GET.get('id', '')
	try:
		pk = int(pk)
	except ValueError:
		return HttpResponseBadRequest()
	return HttpResponsePermanentRedirect(reverse('accounts:profile', kwargs={'pk': pk}))

def article_category_redirect(request, pk):
	category = get_object_or_404(ArticleCategory, pk=pk)
	return HttpResponsePermanentRedirect(reverse('article:list-category', kwargs={'category': category.slug, 'page': 1}))

def news_list_redirect(request, **kwargs):
	kwargs['page'] = 1
	return HttpResponsePermanentRedirect(reverse('news:list', kwargs=kwargs))

def topic_list_redirect(request):
	return HttpResponsePermanentRedirect(reverse('forum:overview', kwargs={'page': 1}))

def comments_redirect(request, pk, parent): # pylint: disable=unused-argument
	return HttpResponsePermanentRedirect(reverse('comments:reply', kwargs={'parent': parent}))

def news_comment_redirect(request, pk):
	news = get_object_or_404(News, pk=pk)
	return HttpResponsePermanentRedirect(reverse('news:detail', kwargs={'slug': news.slug}))

def home_redirect(request, *args, **kwargs):
	return HttpResponsePermanentRedirect(reverse('home'))

def home_temp_redirect(request, *args, **kwargs):
	return HttpResponseRedirect(reverse('home'))

def forum_topic_redirect(request, pk):
	return HttpResponsePermanentRedirect(reverse('forum:topic-detail', kwargs={'pk': pk}))

def forum_category_redirect(request, category, page=None):
	kwargs = {}
	if page:
		kwargs['page'] = page
	else:
		kwargs['page'] = 1
	section = get_object_or_404(ForumSection, pk=category)
	kwargs['category'] = section.slug
	return HttpResponsePermanentRedirect(reverse('forum:section', kwargs=kwargs))

def forum_topic_old_redirect(request):
	try:
		forumid = int(request.GET.get('forumid', 0))
	except ValueError:
		forumid = 0
	return HttpResponsePermanentRedirect(reverse('forum:topic-detail', kwargs={'pk': forumid}))

def news_redirect(request, pk):
	news = get_object_or_404(News, pk=pk)
	return HttpResponsePermanentRedirect(reverse('news:detail', kwargs={'slug': news.slug}))

def poll_redirect(request, pk):
	poll = get_object_or_404(Poll, pk=pk)
	return HttpResponsePermanentRedirect(reverse('polls:detail-by-slug', kwargs={'slug': poll.slug}))

def wiki_redirect(request, pk):
	wiki = get_object_or_404(WikiPage, pk=int(pk) + 7)
	return HttpResponsePermanentRedirect(wiki.get_absolute_url())

def forum_rss_redirect(request):
	return HttpResponsePermanentRedirect(reverse('forum:feed-latest'))

def news_rss_redirect(request):
	return HttpResponsePermanentRedirect(reverse('news:feed-latest'))

def article_rss_redirect(request):
	return HttpResponsePermanentRedirect(reverse('article:feed-latest'))

def eshop_redirect(request, **kwargs):
	return HttpResponseRedirect('http://linuxeshop.eu/')

def old_php_redirect(request): #pylint: disable=too-many-return-statements
	show = request.GET.get('show')
	if show == 'clanok':
		try:
			pk = int(request.GET.get('id', ''))
		except ValueError:
			return HttpResponseBadRequest()
		article = get_object_or_404(Article, pk=pk)
		return HttpResponsePermanentRedirect(reverse('article:detail', kwargs={'slug': article.slug}))
	elif show == 'KnowledgeBase_show_entry':
		try:
			pk = int(request.GET.get('id', ''))
		except ValueError:
			return HttpResponseBadRequest()
		wiki = get_object_or_404(WikiPage, pk=int(pk) + 7)
		return HttpResponsePermanentRedirect(wiki.get_absolute_url())
	elif show == 'autori':
		return HttpResponseRedirect(reverse('home'))
	elif show == 'team':
		return HttpResponsePermanentRedirect(reverse('page_team'))
	elif show == 'odkazy':
		return HttpResponsePermanentRedirect(reverse('page_odkazy'))
	elif show == 'forum_zoznam':
		return HttpResponsePermanentRedirect(reverse('forum:overview', kwargs={'page': 1}))

	return HttpResponseNotFound()

def forum_page_redirect(request, page):
	return HttpResponsePermanentRedirect(reverse('forum:overview', kwargs={'page': page}))

def news_page_redirect(request, page):
	return HttpResponsePermanentRedirect(reverse('news:list', kwargs={'page': page}))
