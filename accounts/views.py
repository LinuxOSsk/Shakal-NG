# -*- coding: utf-8 -*-
from datetime import datetime, time

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.views.generic import RedirectView, DetailView, UpdateView, TemplateView

from .forms import ProfileEditForm, AvatarUpdateForm, PositionUpdateForm
from .models import User
from .stats import register
from comments.models import UserDiscussionAttribute
from common_utils.content_types import resolve_content_objects
from common_utils.generic import ListView
from desktops.models import FavoriteDesktop


User = get_user_model()


class UserZone(LoginRequiredMixin, RedirectView):
	permanent = False
	pattern_name = 'accounts:my_profile'


class Profile(DetailView):
	pattern_name = 'accounts:my_profile'
	template_name = 'account/profile.html'
	context_object_name = 'user_profile'

	def get_queryset(self):
		if self.request.user.is_authenticated and self.request.user.is_superuser:
			return User.objects.all()
		else:
			return User.objects.filter(is_active=True)

	def get_context_data(self, **kwargs):
		ctx = super(Profile, self).get_context_data(**kwargs)
		user = self.object
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
		ctx['favorite_desktops'] = self.get_favorite_desktops()
		return ctx

	def get_favorite_desktops(self):
		return (FavoriteDesktop.objects.all()
			.filter(user=self.object)
			.select_related('desktop')
			.order_by('-pk'))


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


class MyProfileAvatarEdit(LoginRequiredMixin, MyProfileMixin, UpdateView):
	template_name = 'account/profile_avatar_change.html'
	form_class = AvatarUpdateForm

	def get_success_url(self):
		return reverse('accounts:my_profile')


class MyProfilePositionEdit(LoginRequiredMixin, MyProfileMixin, UpdateView):
	template_name = 'account/profile_position_change.html'
	form_class = PositionUpdateForm

	def get_success_url(self):
		return reverse('accounts:my_profile')


class MyWatched(LoginRequiredMixin, ListView):
	template_name = 'account/my_watched.html'
	paginate_by = 50

	def get_queryset(self, *args, **kwargs):
		return (UserDiscussionAttribute.objects
			.filter(user=self.request.user, watch=True)
			.order_by('-pk')
			.values_list('discussion__content_type_id', 'discussion__object_id'))

	def get_context_data(self, **kwargs):
		ctx = super(MyWatched, self).get_context_data(**kwargs)
		ctx['object_list'] = resolve_content_objects(ctx['object_list'])
		return ctx


class MyViewed(LoginRequiredMixin, ListView):
	template_name = 'account/my_viewed.html'
	paginate_by = 50

	def get_queryset(self, *args, **kwargs):
		return (UserDiscussionAttribute.objects
			.filter(user=self.request.user)
			.order_by('-time')
			.values_list('discussion__content_type_id', 'discussion__object_id'))

	def get_context_data(self, **kwargs):
		ctx = super(MyViewed, self).get_context_data(**kwargs)
		ctx['object_list'] = resolve_content_objects(ctx['object_list'])
		return ctx


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
			return reverse('accounts:user_posts_' + view_name, kwargs={'pk': self.object.pk, 'page': 1})

		return (
			{
				'label': stats.get_verbose_name_plural(),
				'count': stats.get_count(),
				'url': url(name),
			}
			for name, stats in register.get_all_statistics(self.object, self.request)
		)

	def get_object(self):
		if self.request.user.is_authenticated and self.request.user.is_superuser:
			queryset = User.objects.all()
		else:
			queryset = User.objects.filter(is_active=True)

		return get_object_or_404(queryset, pk=self.kwargs['pk'])

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
		time_from = datetime.combine(day, time.min).replace(tzinfo=current_timezone)
		time_to = datetime.combine(day, time.max).replace(tzinfo=current_timezone)
		return (time_from, time_to)

	def get(self, request, **kwargs):
		self.object = self.get_object()
		return super(UserStatsMixin, self).get(request, **kwargs)

	def get_queryset(self):
		qs = self.statistics.get_list_queryset()
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
			newest = statistic.get_list_queryset()
			if day_range:
				newest = newest.filter(date_field__range=day_range)
			all_newest += list(newest.order_by('-date_field')[:20])
		all_newest = sorted(all_newest, key=lambda x: getattr(x, 'date_field', None) or x['date_field'], reverse=True)[:20]

		ctype_lookups = [(obj['content_type_id'], obj['object_id'], obj['date_field'], i) for i, obj in enumerate(all_newest) if isinstance(obj, dict)]
		all_newest = [o if isinstance(o, models.Model) else None for o in all_newest]
		if ctype_lookups:
			for lookup, content_object in zip(ctype_lookups, resolve_content_objects(ctype_lookups)):
				if content_object is None:
					continue
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

	def get_context_data(self, **kwargs):
		ctx = super(UserPostsCommented, self).get_context_data(**kwargs)
		objects = resolve_content_objects([(obj['content_type_id'], obj['object_id']) for obj in ctx['object_list']])
		ctx['object_list'] = objects
		return ctx


class UserPostsWikiPage(UserStatsListBase):
	stats_name = 'wikipage'


class UserMap(DetailView):
	context_object_name = 'user_profile'
	model = get_user_model()
	template_name = 'account/user_map.html'


class UsersMap(TemplateView):
	template_name = 'account/users_map.html'

	def get_context_data(self, **kwargs):
		ctx = super(UsersMap, self).get_context_data(**kwargs)
		ctx['users'] = (User.objects.all()
			.filter(is_active=True)
			.exclude(geoposition='')
			.values('pk', 'username', 'geoposition'))
		for user in ctx['users']:
			user['url'] = reverse('accounts:profile', args=[], kwargs={'pk': user['pk']})
		return ctx
