# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.models import ModelForm

from wiki.models import Page


class WikiEditForm(ModelForm):
	class Meta:
		model = Page
		fields = ('title', 'original_text')
