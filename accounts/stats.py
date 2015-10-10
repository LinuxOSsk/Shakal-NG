# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from braces.views import LoginRequiredMixin
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Count, Max
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.views.generic import RedirectView, DetailView, UpdateView
from django.template.defaultfilters import capfirst

from .forms import ProfileEditForm
from common_utils import get_meta
from common_utils.generic import ListView
from common_utils.time_series import time_series, set_gaps_zero


class Statistics(object):
	verbose_name_plural = None

	def __init__(self, user):
		self.user = user

	def get_queryset(self):
		raise NotImplementedError()

	def get_count(self):
		return self.get_queryset().count()

	def get_verbose_name_plural(self):
		return capfirst(self.verbose_name_plural or get_meta(self.get_queryset().model).verbose_name_plural)


class ArticleStatistics(Statistics):
	def get_queryset(self):
		return apps.get_model('article.Article').objects.filter(author=self.user)


class BlogpostStatistics(Statistics):
	def get_queryset(self):
		return apps.get_model('blog.Post').objects.filter(blog__author=self.user)


class ForumtopicStatistics(Statistics):
	def get_queryset(self):
		return apps.get_model('forum.Topic').objects.filter(author=self.user)


class NewsStatistics(Statistics):
	def get_queryset(self):
		return apps.get_model('news.News').objects.filter(author=self.user)


class CommentedStatistics(Statistics):
	def get_queryset(self):
		return (apps.get_model('threaded_comments.Comment')
			.objects
			.filter(user=self.user, parent__isnull=False)
			.values_list('content_type_id', 'object_id')
			.annotate(max_pk=Max('pk'))
			.order_by('-max_pk'))

	def get_verbose_name_plural(self):
		return 'Komentované diskusie'


class WikipageStatistics(Statistics):
	verbose_name_plural = 'Wiki stránky'

	def get_queryset(self):
		return (apps.get_model('wiki.Page')
			.objects
			.filter(last_author=self.user, parent__isnull=False))


STATISTICS = (
	('article', ArticleStatistics),
	('blogpost', BlogpostStatistics),
	('forumtopic', ForumtopicStatistics),
	('news', NewsStatistics),
	('commented', CommentedStatistics),
	('wikipage', WikipageStatistics),
)


class Register(object):
	def get_statistics(self, name, user):
		return dict(STATISTICS)[name](user)

	def get_all_statistics(self, user):
		return tuple((k, v(user)) for k, v in STATISTICS)


register = Register()
