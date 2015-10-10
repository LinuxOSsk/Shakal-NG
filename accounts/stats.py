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
	date_field = None

	def __init__(self, user):
		self.user = user

	def get_queryset(self):
		raise NotImplementedError()

	def get_graph_queryset(self):
		return self.get_queryset()

	def get_count(self):
		return self.get_queryset().count()

	def get_verbose_name_plural(self):
		return capfirst(self.verbose_name_plural or get_meta(self.get_queryset().model).verbose_name_plural)

	@cached_property
	def cached_now(self):
		return timezone.localtime(timezone.now())

	def get_time_series(self, interval, time_stats_ago=365):
		return set_gaps_zero(time_series(
			qs=self.get_graph_queryset(),
			date_field=self.date_field,
			interval=interval,
			aggregate=Count('id'),
			date_from=self.cached_now.date() + timedelta(-time_stats_ago),
			date_to=self.cached_now.date()
		))

	def get_stats(self):
		monthly_stats = self.get_time_series('month', 365*10)
		daily_stats = self.get_time_series('day', 365)
		return {
			'monthly_stats': monthly_stats,
			'daily_stats': daily_stats,
		}


class ArticleStatistics(Statistics):
	date_field = 'pub_time'

	def get_queryset(self):
		return apps.get_model('article.Article').objects.filter(author=self.user)


class BlogpostStatistics(Statistics):
	date_field = 'pub_time'

	def get_queryset(self):
		return apps.get_model('blog.Post').objects.filter(blog__author=self.user)


class ForumtopicStatistics(Statistics):
	date_field = 'created'

	def get_queryset(self):
		return apps.get_model('forum.Topic').objects.filter(author=self.user)


class NewsStatistics(Statistics):
	date_field = 'created'

	def get_queryset(self):
		return apps.get_model('news.News').objects.filter(author=self.user)


class CommentedStatistics(Statistics):
	date_field = 'submit_date'

	def get_queryset(self):
		return (apps.get_model('threaded_comments.Comment')
			.objects
			.filter(user=self.user, parent__isnull=False)
			.values_list('content_type_id', 'object_id')
			.annotate(max_pk=Max('pk'))
			.order_by('-max_pk'))

	def get_graph_queryset(self):
		return (apps.get_model('threaded_comments.Comment')
			.objects
			.filter(parent__isnull=False, user=self.user))

	def get_verbose_name_plural(self):
		return 'Komentované diskusie'


class WikipageStatistics(Statistics):
	verbose_name_plural = 'Wiki stránky'
	date_field = 'updated'

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
