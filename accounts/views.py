# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from braces.views import LoginRequiredMixin
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import RedirectView, DetailView, UpdateView
from common_utils.generic import ListView

from .forms import ProfileEditForm


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


class UserPostsArticle(UserStatsMixin, ListView):
	template_name = 'account/user_posts_article.html'

	def get_queryset(self):
		return self.get_articles().order_by('-pk')
