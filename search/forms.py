# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from haystack.forms import HighlightedModelSearchForm


class SearchForm(HighlightedModelSearchForm):
	def __init__(self, *args, **kwargs):
		super(SearchForm, self).__init__(*args, **kwargs)
		self.fields['models'].label = 'Hľadať v'
		self.fields['models'].choices.sort(key=lambda x: unicode(x[0]))
