# -*- coding: utf-8 -*-

from django.forms.models import ModelForm
from rich_editor.forms import RichOriginalField
from shakal.wiki.models import Page


class WikiEditForm(ModelForm):
	original_text = RichOriginalField(label = u'Text')
	class Meta:
		model = Page
		exclude = ('parent', 'slug', 'page_type', 'last_author')
