# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.models import ModelForm

from common_utils import get_meta
from rich_editor.forms import RichOriginalField
from wiki.models import Page


class WikiEditForm(ModelForm):
	original_text = RichOriginalField(parsers=get_meta(Page).get_field('original_text').parsers, label=u'Text')

	class Meta:
		model = Page
		exclude = ('parent', 'slug', 'page_type', 'last_author', 'filtered_text')
