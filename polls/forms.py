# -*- coding: utf-8 -*-

from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.translation import ugettext_lazy as _
from .models import Choice, Poll
from common_utils.admin_widgets import AutosizedTextarea, DateTimeInput


class BaseChoiceFormSet(BaseFormSet):
	def clean(self):
		if any(self.errors):
			return
		cleaned_data = []
		for i in range(0, self.total_form_count()):
			form = self.forms[i]
			if 'choice' in form.cleaned_data and form.cleaned_data['choice']:
				cleaned_data.append(form.cleaned_data)
		if len(cleaned_data) < 2:
			raise forms.ValidationError(_("Minimum 2 choices are required"))
		return cleaned_data


class ChoiceForm(forms.ModelForm):
	class Meta:
		model = Choice
		exclude = ('poll', 'votes', )

ChoiceFormSet = formset_factory(ChoiceForm, formset = BaseChoiceFormSet, extra = 10)
ChoiceFormSet.label = _('Choices')
ChoiceFormSet.hide_table_labels = True


class PollForm(forms.ModelForm):
	nested = []

	def __init__(self, data = None, *args, **kwargs):
		super(PollForm, self).__init__(data, *args, **kwargs)
		self.nested = [ChoiceFormSet(data)]

	def clean(self):
		cleaned_data = super(PollForm, self).clean()
		cleaned_data['choices'] = self.nested[0].clean()
		return cleaned_data

	class Meta:
		model = Poll
		exclude = ('approved', 'active_from', 'choice_count', 'content_type', 'object_id', 'slug')
		fields = ('question', 'checkbox')


class PollAdminForm(forms.ModelForm):
	class Meta:
		model = Poll
		widgets = {
			'question': AutosizedTextarea(attrs={'class': 'input-xlarge'}),
			'slug': forms.TextInput(attrs={'class': 'input-xlarge'}),
			'active_from': DateTimeInput()
		}
