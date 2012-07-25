# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponsePermanentRedirect
from shakal.article.models import Article

def profile_redirect(request, pk):
	return HttpResponsePermanentRedirect(reverse('auth_profile', kwargs = {'pk': pk}))

def article_redirect(request, pk):
	article = get_object_or_404(Article, pk = pk)
	return HttpResponsePermanentRedirect(reverse('article:detail-by-slug', kwargs = {'slug': article.slug}))
