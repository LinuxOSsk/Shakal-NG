# -*- coding: utf-8 -*-

from django import forms
from django.forms.widgets import RadioSelect

from .models import Rating


class FlagForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		self.object = kwargs.pop('object')
		super().__init__(*args, **kwargs)
		if not self.instance or self.instance.marked_flag == Rating.FLAG_NONE:
			self.fields['marked_flag'].choices = Rating.FLAG_CHOICES[1:]
			self.fields['marked_flag'].required = True
			self.initial['marked_flag'] = Rating.FLAG_SPAM
		if self.data.get(self.add_prefix('marked_flag')) == Rating.FLAG_OTHER:
			self.fields['comment'].required = True

	class Meta:
		model = Rating
		fields = ('marked_flag', 'comment')
		widgets = {
			'marked_flag': RadioSelect(),
		}

	def clean(self):
		cleaned_data = super().clean()
		if cleaned_data.get('marked_flag') == Rating.FLAG_NONE:
			cleaned_data['comment'] = ''
		return cleaned_data

	def save(self):
		return Rating.objects.rate(
			self.object,
			self.user,
			marked_flag=self.cleaned_data['marked_flag'],
			comment=self.cleaned_data['comment']
		)
