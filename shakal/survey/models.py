# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class Survey(models.Model):
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
		return self.answer_set.order_by('pk')

	def clean(self):
		if self.content_type and not self.object_id:
			raise ValidationError(_('Field object id is required'))
		if self.object_id and not self.content_type:
			raise ValidationError(_('Field content type is required'))

	def __unicode__(self):
		return self.question

	class Meta:
		verbose_name = _('survey')
		verbose_name_plural = _('surveys')


class Answer(models.Model):
	survey = models.ForeignKey(Survey)
	answer = models.CharField(max_length = 255)
	votes = models.PositiveIntegerField(default = 0)

	def __unicode__(self):
		return self.answer

	class Meta:
		verbose_name = _('answer')
		verbose_name_plural = _('answers')
