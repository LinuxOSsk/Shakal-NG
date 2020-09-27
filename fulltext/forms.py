# -*- coding: utf-8 -*-
from django import forms
from django.template.defaultfilters import capfirst

from fulltext import registry as fulltext_registry


class SearchForm(forms.Form):
	q = forms.CharField(
		label="Vyhľadávanie",
		required=False
	)
	ordering = forms.ChoiceField(
		label="Zoradiť",
		initial='-rank',
		required=False,
		choices=(
			('-rank', "Podľa relevancie"),
			('-created', "Najnovšie"),
			('created', "Najstaršie"),
			('-updated', "Naposledy aktualizované"),
			('updated', "Najstaršie aktualizované"),
		)
	)
	content = forms.MultipleChoiceField(
		label="Obsah",
		required=False,
		widget=forms.CheckboxSelectMultiple,
		choices=(
			('document', "Dokument"),
			('comments', "Komentáre")
		)
	)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		model_choices = []
		for index in fulltext_registry:
			model = index.model
			meta = model._meta
			model_choices.append((meta.app_label + '.' + meta.model_name, capfirst(meta.verbose_name_plural)))
		self.fields['models'] = forms.MultipleChoiceField(
			label="Hľadať v",
			choices=model_choices,
			widget=forms.CheckboxSelectMultiple,
			required=False,
			help_text="Ponechajte všetky políčka prázdne, ak chcete vyhľadávať v kompletnom obsahu"
		)
