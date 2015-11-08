# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from datetime import datetime, time
from braces.views import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.views.generic import RedirectView, DetailView, UpdateView

from .forms import ProfileEditForm
from .stats import register
from common_utils.content_types import resolve_content_objects
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

	def get_context_data(self, **kwargs):
		ctx = super(UserStatsMixin, self).get_context_data(**kwargs)
		ctx['user_profile'] = self.object
		ctx['day'] = self.get_day()
		return ctx

	def get_all_stats(self):
		def url(view_name):
			return reverse('accounts:user_posts_' + view_name, args=(self.object.pk,), kwargs={})

		return (
			{
				'label': stats.get_verbose_name_plural(),
				'count': stats.get_count(),
				'url': url(name),
			}
			for name, stats in register.get_all_statistics(self.object, self.request)
		)

	def get_object(self):
		return get_object_or_404(get_user_model(), pk=self.kwargs['pk'])

	def get_day(self):
		if not 'day' in self.request.GET:
			return None
		day = self.request.GET['day']
		try:
			return datetime.strptime(day, '%Y-%m-%d').date()
		except ValueError:
			return None

	def get_day_range(self):
		day = self.get_day()
		if day is None:
			return None

		current_timezone = timezone.get_current_timezone()
		time_from = current_timezone.localize(datetime.combine(day, time.min))
		time_to = current_timezone.localize(datetime.combine(day, time.max))
		return (time_from, time_to)

	def get(self, request, **kwargs):
		self.object = self.get_object()
		return super(UserStatsMixin, self).get(request, **kwargs)

	def get_queryset(self):
		qs = self.get_list_queryset()
		day_range = self.get_day_range()
		if day_range:
			qs = qs.filter(date_field__range=day_range)
		return qs


class UserPosts(UserStatsMixin, DetailView):
	template_name = 'account/user_posts.html'

	def get_stats_summary(self):
		stats_sum = None
		for _, statistic in register.get_all_statistics(self.object, self.request):
			if stats_sum is None:
				stats_sum = statistic.get_stats()
			else:
				stats = statistic.get_stats()
				for key in stats:
					stats_sum[key] = [a._replace(aggregate=a.aggregate + b.aggregate) for a, b in zip(stats_sum[key], stats[key])]
		return stats_sum

	def get_last_contributions(self):
		all_newest = []
		day_range = self.get_day_range()
		for _, statistic in register.get_all_statistics(self.object, self.request):
			newest = statistic.get_time_annotated_queryset()
			if day_range:
				newest = newest.filter(date_field__range=day_range)
			all_newest += list(newest.order_by('-date_field')[:20])
		all_newest = sorted(all_newest, key=lambda x: getattr(x, 'date_field', None) or x['date_field'], reverse=True)[:20]

		ctype_lookups = [(obj['content_type_id'], obj['object_id'], obj['date_field'], i) for i, obj in enumerate(all_newest) if isinstance(obj, dict)]
		if ctype_lookups:
			for lookup, content_object in zip(ctype_lookups, resolve_content_objects(ctype_lookups)):
				setattr(content_object, 'from_comments', True)
				setattr(content_object, 'date_field', lookup[2])
				all_newest[lookup[3]] = content_object
		return all_newest

	def get_context_data(self, **kwargs):
		ctx = super(UserPosts, self).get_context_data(**kwargs)
		ctx['stats'] = self.get_all_stats()
		ctx['last_contributions'] = self.get_last_contributions()
		ctx.update(self.get_stats_summary())
		return ctx


class UserStatsListBase(UserStatsMixin, ListView):
	template_name = 'account/user_posts_detail.html'
	stats_name = ''

	@cached_property
	def statistics(self):
		return register.get_statistics(self.stats_name, self.object, self.request)

	def get_objects_name(self):
		return self.statistics.get_verbose_name_plural()

	def get_context_data(self, **kwargs):
		ctx = super(UserStatsListBase, self).get_context_data(**kwargs)
		if self.stats_name:
			ctx.update(self.statistics.get_stats())
			ctx['objects_name'] = self.get_objects_name()
		return ctx

	def get_list_queryset(self):
		return self.statistics.get_time_annotated_queryset().order_by('-pk')


class UserPostsArticle(UserStatsListBase):
	stats_name = 'article'


class UserPostsBlogpost(UserStatsListBase):
	stats_name = 'blogpost'


class UserPostsNews(UserStatsListBase):
	stats_name = 'news'


class UserPostsForumTopic(UserStatsListBase):
	stats_name = 'forumtopic'


class UserPostsCommented(UserStatsListBase):
	template_name = 'account/user_posts_commented.html'
	stats_name = 'commented'

	def get_list_queryset(self):
		return (self.statistics
			.get_time_annotated_queryset()
			.order_by('-max_pk')
			.values_list('content_type_id', 'object_id'))

	def get_context_data(self, **kwargs):
		ctx = super(UserPostsCommented, self).get_context_data(**kwargs)
		objects = resolve_content_objects(ctx['object_list'])
		ctx['object_list'] = objects
		return ctx


class UserPostsWikiPage(UserStatsListBase):
	stats_name = 'wikipage'
