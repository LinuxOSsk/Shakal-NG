# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import permalink
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from autoslugfield.fields import AutoSlugField


class PollListManager(models.Manager):
	def get_query_set(self):
		return super(PollListManager, self) \
			.get_query_set() \
			.filter(approved=True, active_from__lte=timezone.now(), content_type_id=None) \
			.order_by("-active_from")


class Poll(models.Model):
	all_objects = models.Manager()
	objects = PollListManager()

	question = models.TextField(_("question"))
	slug = AutoSlugField(unique=True, title_field='question')

	content_type = models.ForeignKey(ContentType, limit_choices_to={"model__in": ("article",)}, null=True, blank=True, verbose_name=_("content type"))
	object_id = models.PositiveIntegerField(verbose_name=_("object id"), null=True, blank=True)
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	active_from = models.DateTimeField(verbose_name=_("active from"), blank=True, null=True)
	checkbox = models.BooleanField(_("more choices"), default=False)
	approved = models.BooleanField(_("approved"), default=False)

	choice_count = models.PositiveIntegerField(default=0)

	@property
	def choices(self):
		return Choice.objects.filter(poll=self.pk).select_related('poll__choice_count').order_by('pk')

	@permalink
	def get_absolute_url(self):
		return ('polls:detail-by-slug', None, {'slug': self.slug})

	@permalink
	def get_list_url(self):
		return ('polls:list', None, None)

	def msg_id(self):
		return 'poll-' + str(self.pk)

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
		verbose_name = _('poll')
		verbose_name_plural = _('polls')


class Choice(models.Model):
	poll = models.ForeignKey(Poll, verbose_name=_("poll"))
	choice = models.CharField(_("poll choice"), max_length=255)
	votes = models.PositiveIntegerField(_("votes"), default=0)

	def percent(self):
		if self.poll.choice_count == 0:
			return 0
		else:
			return 100.0 * self.votes / self.poll.choice_count

	def __unicode__(self):
		return self.choice

	class Meta:
		verbose_name = _('choice')
		verbose_name_plural = _('choices')


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


def check_can_vote(request, poll):
	if request.user.is_authenticated():
		return not RecordUser.objects.filter(user=request.user, poll=poll).exists()
	else:
		return not RecordIp.objects.filter(ip=request.META['REMOTE_ADDR'], poll=poll).exists()


def record_vote(request, poll):
	if request.user.is_authenticated():
		RecordUser(user=request.user, poll=poll).save()
	else:
		RecordIp(ip=request.META['REMOTE_ADDR'], poll=poll).save()
