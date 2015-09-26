# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from haystack.forms import HighlightedModelSearchForm


class SearchForm(HighlightedModelSearchForm):
	ORDERING_DEFAULT = ''
	ORDERING_NEW_CREATED = 'nc'
	ORDERING_OLD_CREATED = 'oc'
	ORDERING_NEW_UPDATED = 'nu'
	ORDERING_OLD_UPDATED = 'ou'

	ORDERING_CHOICES = (
		(ORDERING_DEFAULT, 'Podľa relevancie'),
		(ORDERING_NEW_CREATED, 'Najnovšie'),
		(ORDERING_OLD_CREATED, 'Najstaršie'),
		(ORDERING_NEW_UPDATED, 'Naposledy aktualizované'),
		(ORDERING_OLD_UPDATED, 'Najstaršie aktualizované'),
	)

	ordering = forms.ChoiceField(choices=ORDERING_CHOICES, required=False, label='Zoradiť')

	def __init__(self, *args, **kwargs):
		super(SearchForm, self).__init__(*args, **kwargs)
		self.fields['models'].label = 'Hľadať v'
		self.fields['models'].choices.sort(key=lambda x: unicode(x[0]))

	def search(self):
		cleaned_data = self.cleaned_data
		ordering = cleaned_data.get('ordering')
		sqs = super(SearchForm, self).search()
		if ordering == self.ORDERING_DEFAULT:
			pass
		elif ordering == self.ORDERING_NEW_CREATED:
			sqs = sqs.order_by('-created')
		elif ordering == self.ORDERING_OLD_CREATED:
			sqs = sqs.order_by('created')
		elif ordering == self.ORDERING_NEW_UPDATED:
			sqs = sqs.order_by('-updated')
		elif ordering == self.ORDERING_OLD_UPDATED:
			sqs = sqs.order_by('updated')
		return sqs
