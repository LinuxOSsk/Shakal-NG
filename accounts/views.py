# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
			for name, stats in register.get_all_statistics(self.object)
		)

	def get_object(self):
		return get_object_or_404(get_user_model(), pk=self.kwargs['pk'])

	def get(self, request, **kwargs):
		self.object = self.get_object()
		return super(UserStatsMixin, self).get(request, **kwargs)


class UserPosts(UserStatsMixin, DetailView):
	template_name = 'account/user_posts.html'

	def get_stats_summary(self):
		stats_sum = None
		for _, statistic in register.get_all_statistics(self.object):
			if stats_sum is None:
				stats_sum = statistic.get_stats()
			else:
				stats = statistic.get_stats()
				for key in stats:
					stats_sum[key] = [a._replace(aggregate=a.aggregate + b.aggregate) for a, b in zip(stats_sum[key], stats[key])]
		return stats_sum


	def get_context_data(self, **kwargs):
		ctx = super(UserPosts, self).get_context_data(**kwargs)
		ctx['stats'] = self.get_all_stats()
		ctx.update(self.get_stats_summary())
		return ctx


class UserStatsListBase(UserStatsMixin, ListView):
	template_name = 'account/user_posts_detail.html'
	stats_name = ''

	@cached_property
	def statistics(self):
		return register.get_statistics(self.stats_name, self.object)

	def get_objects_name(self):
		return self.statistics.get_verbose_name_plural()

	def get_context_data(self, **kwargs):
		ctx = super(UserStatsListBase, self).get_context_data(**kwargs)
		if self.stats_name:
			ctx.update(self.statistics.get_stats())
			ctx['objects_name'] = self.get_objects_name()
		return ctx

	def get_queryset(self):
		return self.statistics.get_queryset().order_by('-pk')


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

	def get_queryset(self):
		return self.statistics.get_queryset().order_by('-max_pk')

	def get_context_data(self, **kwargs):
		ctx = super(UserPostsCommented, self).get_context_data(**kwargs)
		objects = resolve_content_objects(ctx['object_list'])
		ctx['object_list'] = objects['list']
		ctx['object_list_by_content'] = objects['by_content']
		return ctx


class UserPostsWikiPage(UserStatsListBase):
	stats_name = 'wikipage'
