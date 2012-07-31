# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponsePermanentRedirect
from shakal.article.models import Article
from shakal.news.models import News
from shakal.survey.models import Survey

def profile_redirect(request, pk):
	return HttpResponsePermanentRedirect(reverse('auth_profile', kwargs = {'pk': pk}))

def article_redirect(request, pk):
	article = get_object_or_404(Article, pk = pk)
	return HttpResponsePermanentRedirect(reverse('article:detail-by-slug', kwargs = {'slug': article.slug}))

def forum_topic_redirect(request, pk):
	return HttpResponsePermanentRedirect(reverse('forum:topic-detail', kwargs = {'pk': pk}))

def news_redirect(request, pk):
	news = get_object_or_404(News, pk = pk)
	return HttpResponsePermanentRedirect(reverse('news:detail-by-slug', kwargs = {'slug': news.slug}))

def survey_redirect(request, pk):
	survey = get_object_or_404(Survey, pk = pk)
	return HttpResponsePermanentRedirect(reverse('survey:detail-by-slug', kwargs = {'slug': survey.slug}))
