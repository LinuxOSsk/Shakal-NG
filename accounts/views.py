# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from dateutil.relativedelta import relativedelta
from braces.views import LoginRequiredMixin
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db.models import Count, Max
from django.db.models.expressions import DateTime
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.utils.timezone import get_current_timezone, now
from django.views.generic import RedirectView, DetailView, UpdateView

from .forms import ProfileEditForm
from common_utils.generic import ListView


class UserZone(LoginRequiredMixin, RedirectView):
	permanent = False
	pattern_url = 'accounts:my_profile'


class Profile(DetailView):
	pattern_url = 'accounts:my_profile'
	model = get_user_model()
	template_name = 'account/profile.html'
	context_object_name = 'user_profile'

	def get_context_data(self, **kwargs):
		ctx = super(Profile, self).get_context_data(**kwargs)
		user = self.get_object()
		user_table = (
			{'name': 'Používateľské meno', 'value': user.username, 'class': 'nickname'},
			{'name': 'Celé meno', 'value': (user.first_name + ' ' + user.last_name).strip(), 'class': 'fn'},
			{'name': 'Podpis', 'value': mark_safe(user.signature), 'class': ''},
			{'name': 'Linuxová distribúcia', 'value': user.distribution, 'class': 'note'},
			{'name': 'Rok narodenia', 'value': user.year},
		)
		if user.display_mail:
			email = user.email.replace('@', ' ZAVINÁČ ').replace('.', ' BODKA ')
			user_table = user_table + ({'name': 'E-mail', 'value': email}, )
		ctx['user_table'] = user_table
		ctx['is_my_profile'] = self.request.user.pk == user.pk
		return ctx

class MyProfileMixin(object):
	def get_object(self):
		return self.request.user


class MyProfile(LoginRequiredMixin, MyProfileMixin, Profile):
	pass


class MyProfileEdit(LoginRequiredMixin, MyProfileMixin, UpdateView):
	template_name = 'account/profile_change.html'
	form_class = ProfileEditForm

	def get_success_url(self):
		return reverse('accounts:my_profile')


class UserStatsMixin(object):
	paginate_by = 50
	object = None

	def get_articles(self):
		return apps.get_model('article.Article').objects.filter(author=self.object)

	def get_blog_posts(self):
		return apps.get_model('blog.Post').objects.filter(blog__author=self.object)

	def get_forum_topics(self):
		return apps.get_model('forum.Topic').objects.filter(author=self.object)

	def get_news(self):
		return apps.get_model('news.News').objects.filter(author=self.object)

	def get_commented(self):
		return (apps.get_model('threaded_comments.Comment')
			.objects
			.values_list('content_type_id', 'object_id')
			.annotate(last_updated=Max('updated'))
			.order_by('-last_updated'))

	def get_object(self):
		return get_object_or_404(get_user_model(), pk=self.kwargs['pk'])

	def get_last_updated_wiki_pages(self):
		return (apps.get_model('wiki.Page')
			.objects
			.filter(last_author=self.object, parent__isnull=False))

	def get_context_data(self, **kwargs):
		ctx = super(UserStatsMixin, self).get_context_data(**kwargs)
		ctx['user_profile'] = self.object
		return ctx

	def get(self, request, **kwargs):
		self.object = self.get_object()
		return super(UserStatsMixin, self).get(request, **kwargs)


class UserPosts(UserStatsMixin, DetailView):
	template_name = 'account/user_posts.html'

	def get_context_data(self, **kwargs):
		def url(view_name):
			return reverse('accounts:user_posts_' + view_name, args=(self.object.pk,), kwargs={})

		ctx = super(UserPosts, self).get_context_data(**kwargs)
		ctx['stats'] = (
			{'label': 'Články', 'url': url('article'), 'count': self.get_articles().count()},
			{'label': 'Blogy', 'count': self.get_blog_posts().count()},
			{'label': 'Správy', 'count': self.get_news().count()},
			{'label': 'Témy vo fóre', 'count': self.get_forum_topics().count()},
			{'label': 'Komentované diskusie', 'count': self.get_commented().count()},
			{'label': 'Wiki stránky', 'count': self.get_last_updated_wiki_pages().count()},
		)
		return ctx


class UserStatsListBase(UserStatsMixin, ListView):
	stats_by_date_field = None

	def fill_time_series_gap(self, time_series, interval, last_time=None):
		time_series = list(time_series)
		if len(time_series) < 2:
			return time_series

		time_series_filled = []
		for series_item in time_series:
			item_time = series_item[0]

			if last_time is not None:
				last_time += relativedelta(**{interval: 1})
				while last_time < item_time:
					last_time += relativedelta(**{interval: 1})
					time_series_filled.append((last_time, 0))

			time_series_filled.append(series_item)
			last_time = item_time
		return time_series_filled

	def get_time_series(self, interval, time_stats_ago=365):
		return (self.get_queryset()
			.filter(**{self.stats_by_date_field + '__gte': now().date() + timedelta((-365) * 10)})
			.annotate(**{interval: DateTime(self.stats_by_date_field, interval, get_current_timezone())})
			.values(interval)
			.annotate(count=Count('id'))
			.order_by(interval)
			.values_list(interval, 'count'))

	def get_stats_by_date(self):
		monthly_stats = self.get_time_series('month', 365*10)
		daily_stats = self.get_time_series('day', 365)
		return {
			'monthly_stats': self.fill_time_series_gap(monthly_stats, 'months'),
			'daily_stats': self.fill_time_series_gap(daily_stats, 'days'),
		}

	def get_context_data(self, **kwargs):
		ctx = super(UserStatsListBase, self).get_context_data(**kwargs)
		if self.stats_by_date_field is not None:
			ctx.update(self.get_stats_by_date())
		return ctx


class UserPostsArticle(UserStatsListBase):
	template_name = 'account/user_posts_article.html'
	stats_by_date_field = 'pub_time'

	def get_queryset(self):
		return self.get_articles().order_by('-pk')
