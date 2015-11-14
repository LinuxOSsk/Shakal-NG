# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_autoslugfield.fields import AutoSlugField

from comments.models import RootHeader, Comment
from common_utils.models import TimestampModelMixin


class ActivePollsListManager(models.Manager):
	def get_queryset(self):
		return super(ActivePollsListManager, self) \
			.get_queryset() \
			.filter(approved=True, active_from__lte=timezone.now()) \
			.order_by('-active_from')


class PollListManager(ActivePollsListManager):
	def get_queryset(self):
		return super(PollListManager, self) \
			.get_queryset() \
			.filter(content_type_id=None)


class Poll(TimestampModelMixin, models.Model):
	all_objects = models.Manager()
	objects = PollListManager()
	active_polls = ActivePollsListManager()

	question = models.TextField('otázka')
	slug = AutoSlugField(unique=True, title_field='question')

	content_type = models.ForeignKey(ContentType, limit_choices_to={'model__in': ('article',)}, null=True, blank=True, verbose_name='typ obsahu')
	object_id = models.PositiveIntegerField(verbose_name='id objektu', null=True, blank=True)
	content_object = GenericForeignKey('content_type', 'object_id')

	active_from = models.DateTimeField(verbose_name='aktívne od', blank=True, null=True)
	checkbox = models.BooleanField('viac odpovedí', default=False)
	approved = models.BooleanField('schválené', default=False)

	answer_count = models.PositiveIntegerField(default=0)

	comments = GenericRelation(Comment)
	comments_header = GenericRelation(RootHeader)

	@property
	def choices(self):
		return Choice.objects.filter(poll=self.pk).select_related('poll__choice_count').order_by('pk')

	@models.permalink
	def get_absolute_url(self):
		return ('polls:detail-by-slug', None, {'slug': self.slug})

	@models.permalink
	def get_list_url(self):
		return ('polls:list', None, None)

	def msg_id(self):
		return 'poll-' + str(self.pk)

	def can_vote(self, request):
		if request.user.is_authenticated():
			return not RecordUser.objects.filter(user=request.user, poll=self).exists()
		else:
			return not RecordIp.objects.filter(ip=request.META['REMOTE_ADDR'], poll=self).exists()

	def record_vote(self, request):
		if request.user.is_authenticated():
			RecordUser(user=request.user, poll=self).save()
		else:
			RecordIp(ip=request.META['REMOTE_ADDR'], poll=self).save()

	def clean(self):
		if self.content_type and not self.object_id:
			raise ValidationError('Pole id objektu je povinné')
		if self.object_id and not self.content_type:
			raise ValidationError('Pole typ obsahu je povinné')
		if self.content_type:
			self.slug = self.content_type.model + '-' + str(self.object_id)

	def __unicode__(self):
		return self.question

	class Meta:
		verbose_name = 'anketa'
		verbose_name_plural = 'ankety'


class Choice(models.Model):
	poll = models.ForeignKey(Poll, verbose_name='anketa')
	choice = models.CharField('odpoveď', max_length=255)
	votes = models.PositiveIntegerField('hlasov', default=0)

	def percent(self):
		if self.poll.answer_count == 0:
			return 0
		else:
			return 100.0 * self.votes / self.poll.answer_count

	def __unicode__(self):
		return self.choice

	class Meta:
		verbose_name = 'odpoveď'
		verbose_name_plural = 'odpovede'


class RecordIp(models.Model):
	poll = models.ForeignKey(Poll)
	ip = models.GenericIPAddressField()
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('poll', 'ip', )

	def __unicode__(self):
		return str(self.poll.pk) + ' - ' + str(self.ip)


class RecordUser(models.Model):
	poll = models.ForeignKey(Poll)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('poll', 'user', )

	def __unicode__(self):
		return str(self.poll.pk) + ' - ' + str(self.user.pk)


def record_vote(request, poll):
	if request.user.is_authenticated():
		RecordUser(user=request.user, poll=poll).save()
	else:
		RecordIp(ip=request.META['REMOTE_ADDR'], poll=poll).save()
