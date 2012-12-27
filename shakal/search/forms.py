# -*- coding: utf-8 -*-

from haystack.forms import ModelSearchForm

class SearchForm(ModelSearchForm):
	def __init__(self, *args, **kwargs):
		super(SearchForm, self).__init__(*args, **kwargs)
		self.fields['models'].label = u"Hľadať v"
