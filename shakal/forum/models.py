# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.db import connection, models
from django.db.models import permalink
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
from generic_aggregation import generic_annotate
from shakal.threaded_comments.models import RootHeader

class Section(models.Model):
	name = models.CharField(max_length = 255, verbose_name = _('name'))
	slug = models.SlugField(unique = True)
	description = models.TextField(verbose_name = _('description'))

	def clean(self):
		slug_num = None
		try:
			slug_num = int(self.slug)
		except:
			pass
		if slug_num is not None:
			raise ValidationError(_('Numeric slug values are not allowed'))

	@permalink
	def get_absolute_url(self):
		return ('forum:section', None, {'section': self.slug})

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = _('section')
		verbose_name_plural = _('sections')


class TopicManager(models.Manager):
	def get_query_set(self):
		return super(TopicManager, self).get_query_set().select_related('user', 'section')


class TopicListManager(models.Manager):
	def get_query_set(self):
		if connection.vendor == 'postgresql':
			queryset = QuerySet(TopicReverseView, using = self._db)
			queryset = queryset.extra(select = {'last_comment': 'last_comment', 'comment_count': 'comment_count'})
		else:
			queryset = QuerySet(Topic, using = self._db)
			queryset = generic_annotate(queryset, RootHeader, models.Max('comments_header__last_comment'), alias = 'last_comment')
			queryset = generic_annotate(queryset, RootHeader, models.Max('comments_header__comment_count'), alias = 'comment_count')
		return queryset

	def newest_comments(self):
		return self.get_query_set().order_by('-last_comment')

	def no_comments(self):
		return self.get_query_set().extra(where = ['comment_count = %s', 'last_comment > %s'], params = [0, datetime.now() - timedelta(60)])

	def most_commented(self):
		return self.get_query_set().extra(where = ['last_comment > %s'], params = [datetime.now() - timedelta(30)], order_by = ['-comment_count'])


class TopicAbstract(models.Model):
	objects = TopicManager()
	topics = TopicListManager()

	section = models.ForeignKey(Section, verbose_name = _('section'))
	subject = models.CharField(max_length = 100, verbose_name = _('subject'))
	text = models.TextField(verbose_name = _('text'))
	time = models.DateTimeField(default = datetime.now, verbose_name = _('time'))
	username = models.CharField(max_length = 50, blank = False, verbose_name = _('user name'))
	user = models.ForeignKey(User, blank = True, null = True, verbose_name = _('user'))
	comments_header = generic.GenericRelation(RootHeader)
	breadcrumb_label = _('forum')

	def get_username(self):
		if self.user:
			if self.user.get_full_name():
				return self.user.get_full_name()
			else:
				return self.user.username
		else:
			return self.username
	get_username.short_description = _('user name')

	@permalink
	def get_absolute_url(self):
		return ('forum:topic-detail', None, {'pk': self.pk})

	@permalink
	def get_list_url(self):
		return ('forum:overview', None, None)

	def __unicode__(self):
		return self.subject

	class Meta:
		abstract = True


class Topic(TopicAbstract):
	class Meta:
		verbose_name = _('topic')
		verbose_name_plural = _('topics')


class TopicView(TopicAbstract):
	class Meta:
		managed = False


class TopicReverseView(TopicAbstract):
	class Meta:
		managed = False
