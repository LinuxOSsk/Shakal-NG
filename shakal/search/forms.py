# -*- coding: utf-8 -*-

from haystack.forms import HighlightedModelSearchForm

class SearchForm(HighlightedModelSearchForm):
	def __init__(self, *args, **kwargs):
		super(SearchForm, self).__init__(*args, **kwargs)
		self.fields['models'].label = u"Hľadať v"
