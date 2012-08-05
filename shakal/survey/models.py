# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import connection, models
from django.db.models import permalink
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from generic_aggregation import generic_annotate
from shakal.threaded_comments.models import RootHeader

class SurveyAbstract(models.Model):
	question = models.TextField(verbose_name = _("question"))
	slug = models.SlugField(unique = True)
	checkbox = models.BooleanField(default = False, verbose_name = _("more answers"))
	approved = models.BooleanField(default = False, verbose_name = _("approved"))
	active_from = models.DateTimeField(blank = True, null = True, verbose_name = _("active from"))
	answer_count = models.PositiveIntegerField(default = 0)

	content_type = models.ForeignKey(ContentType, limit_choices_to = {"model__in": ("article",)}, null = True, blank = True, verbose_name = _("content type"))
	object_id = models.PositiveIntegerField(null = True, blank = True, verbose_name = _("object id"))
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	@property
	def answers(self):
		return Answer.objects.filter(survey = self.pk).select_related('survey__answer_count').order_by('pk')

	@permalink
	def get_absolute_url(self):
		return ('survey:detail-by-slug', None, {'slug': self.slug})

	def msg_id(self):
		return 'survey-' + str(self.pk)

	def clean(self):
		if self.content_type and not self.object_id:
			raise ValidationError(_('Field object id is required'))
		if self.object_id and not self.content_type:
			raise ValidationError(_('Field content type is required'))
		if self.content_type:
			self.slug = self.content_type.model + '-' + str(self.object_id)

	def __unicode__(self):
		return self.question

	class Meta:
		abstract = True


class SurveyListManager(models.Manager):
	def get_query_set(self):
		if connection.vendor == 'postgresql':
			queryset = QuerySet(SurveyView, using = self._db)
			queryset = queryset.extra(select = {'last_comment': 'last_comment', 'comment_count': 'comment_count'})
		else:
			queryset = QuerySet(Survey, using = self._db)
			queryset = generic_annotate(queryset, RootHeader, models.Max('comments_header__last_comment'), alias = 'last_comment')
			queryset = generic_annotate(queryset, RootHeader, models.Max('comments_header__comment_count'), alias = 'comment_count')
		return queryset


class Survey(SurveyAbstract):
	objects = models.Manager()
	surveys = SurveyListManager()

	class Meta:
		verbose_name = _('survey')
		verbose_name_plural = _('surveys')


class SurveyView(SurveyAbstract):
	class Meta:
		managed = False


class Answer(models.Model):
	survey = models.ForeignKey(Survey)
	answer = models.CharField(max_length = 255)
	votes = models.PositiveIntegerField(default = 0)

	def percent(self):
		if self.survey.answer_count == 0:
			return 0
		else:
			return 100.0 * self.votes / self.survey.answer_count

	def __unicode__(self):
		return self.answer

	class Meta:
		verbose_name = _('answer')
		verbose_name_plural = _('answers')


class RecordIp(models.Model):
	survey = models.ForeignKey(Survey)
	ip = models.GenericIPAddressField()
	date = models.DateTimeField(auto_now_add = True)

	class Meta:
		unique_together = ('survey', 'ip', )


class RecordUser(models.Model):
	survey = models.ForeignKey(Survey)
	user = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add = True)

	class Meta:
		unique_together = ('survey', 'user', )


def check_can_vote(request, survey):
	if request.user.is_authenticated():
		return not RecordUser.objects.filter(user = request.user, survey = survey).exists()
	else:
		return not RecordIp.objects.filter(ip = request.META['REMOTE_ADDR'], survey = survey).exists()


def record_vote(request, survey):
	if request.user.is_authenticated():
		RecordUser(user = request.user, survey = survey).save()
	else:
		RecordIp(ip = request.META['REMOTE_ADDR'], survey = survey).save()
