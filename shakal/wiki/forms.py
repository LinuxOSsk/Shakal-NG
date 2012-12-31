# -*- coding: utf-8 -*-

from django.forms.models import ModelForm
from html_editor.fields import HtmlField
from shakal.wiki.models import Page


class WikiEditForm(ModelForm):
	text = HtmlField(label = u'Text')
	class Meta:
		model = Page
		exclude = ('parent', 'slug', 'page_type', 'last_author')
