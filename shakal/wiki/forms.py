# -*- coding: utf-8 -*-

from django.forms.models import ModelForm
from rich_editor.forms import RichTextField
from shakal.wiki.models import Page


class WikiEditForm(ModelForm):
	text = RichTextField(label = u'Text')
	class Meta:
		model = Page
		exclude = ('parent', 'slug', 'page_type', 'last_author')
