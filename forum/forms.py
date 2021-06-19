# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings

from .models import Topic
from antispam.forms import AntispamFormMixin
from attachment.forms import AttachmentFormMixin
from common_utils.forms import AuthorsNameFormMixin
from common_utils.widgets import DescriptionRadioSelect


COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class TopicForm(AntispamFormMixin, AuthorsNameFormMixin, AttachmentFormMixin, forms.ModelForm):
	def get_model(self):
		return Topic

	def security_errors(self):
		return []

	class Meta:
		model = Topic
		fields = ('section', 'authors_name', 'title', 'original_text', )
		widgets = {'section': DescriptionRadioSelect()}
