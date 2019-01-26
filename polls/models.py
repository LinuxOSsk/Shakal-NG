# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django_autoslugfield.fields import AutoSlugField

from common_utils.models import TimestampModelMixin


class ActivePollsListManager(models.Manager):
	def get_queryset(self):
		return (super().get_queryset()
			.filter(approved=True, active_from__lte=timezone.now())
			.order_by('-active_from'))


class PollListManager(ActivePollsListManager):
	def get_queryset(self):
		return (super().get_queryset()
			.filter(content_type_id=None))


class Poll(TimestampModelMixin, models.Model):
	all_objects = models.Manager()
	objects = PollListManager()
	active_polls = ActivePollsListManager()

	question = models.TextField(
		verbose_name="otázka"
	)
	slug = AutoSlugField(
		verbose_name="skratka URL",
		title_field='question',
		unique=True
	)

	content_type = models.ForeignKey(
		ContentType,
		verbose_name="typ obsahu",
		limit_choices_to = (
			Q(app_label='article', model='article') |
			Q(app_label='blog', model='post')
		),
		null=True,
		blank=True,
		on_delete=models.PROTECT
	)
	object_id = models.PositiveIntegerField(
		verbose_name="id objektu",
		null=True,
		blank=True
	)
	content_object = GenericForeignKey('content_type', 'object_id')

	active_from = models.DateTimeField(
		verbose_name="aktívne od",
		blank=True,
		null=True
	)
	checkbox = models.BooleanField(
		verbose_name="viac odpovedí",
		default=False
	)
	approved = models.BooleanField(
		verbose_name="schválené",
		default=False
	)

	answer_count = models.PositiveIntegerField(
		verbose_name="počet odpovedí",
		default=0
	)

	comments = GenericRelation('comments.Comment')
	comments_header = GenericRelation('comments.RootHeader')

	@property
	def choices(self):
		return (Choice.objects
			.filter(poll=self.pk)
			.select_related('poll')
			.order_by('pk'))

	def get_absolute_url(self):
		return reverse('polls:detail-by-slug', kwargs={'slug': self.slug})

	def get_list_url(self):
		return reverse('polls:list', kwargs={'page': 1})

	def msg_id(self):
		return 'poll-' + str(self.pk)

	def can_vote(self, request):
		if request.user.is_authenticated:
			return not RecordUser.objects.filter(user=request.user, poll=self).exists()
		else:
			return not RecordIp.objects.filter(ip=request.META['REMOTE_ADDR'], poll=self).exists()

	def record_vote(self, request):
		if request.user.is_authenticated:
			RecordUser.objects.create(user=request.user, poll=self)
		else:
			RecordIp.objects.create(ip=request.META['REMOTE_ADDR'], poll=self)

	def clean(self):
		if self.content_type and not self.object_id:
			raise ValidationError("Pole id objektu je povinné")
		if self.object_id and not self.content_type:
			raise ValidationError("Pole typ obsahu je povinné")
		if self.content_type:
			self.slug = self.content_type.model + '-' + str(self.object_id)

	def __str__(self):
		return self.question

	class Meta:
		verbose_name = "anketa"
		verbose_name_plural = "ankety"


class Choice(models.Model):
	poll = models.ForeignKey(
		Poll,
		verbose_name="anketa",
		on_delete=models.CASCADE
	)
	choice = models.CharField(
		verbose_name="odpoveď",
		max_length=255
	)
	votes = models.PositiveIntegerField(
		verbose_name="hlasov",
		default=0
	)

	def percent(self):
		if self.poll.answer_count == 0:
			return 0
		else:
			return 100.0 * self.votes / self.poll.answer_count

	def __str__(self):
		return self.choice

	class Meta:
		verbose_name = "odpoveď"
		verbose_name_plural = "odpovede"


class RecordIp(models.Model):
	poll = models.ForeignKey(
		Poll,
		on_delete=models.CASCADE
	)
	ip = models.GenericIPAddressField(
	)
	date = models.DateTimeField(
		auto_now_add=True
	)

	class Meta:
		unique_together = ('poll', 'ip', )

	def __str__(self):
		return str(self.poll.pk) + ' - ' + str(self.ip)


class RecordUser(models.Model):
	poll = models.ForeignKey(
		Poll,
		on_delete=models.CASCADE
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE
	)
	date = models.DateTimeField(
		auto_now_add=True
	)

	class Meta:
		unique_together = ('poll', 'user', )

	def __str__(self):
		return str(self.poll.pk) + ' - ' + str(self.user.pk)
