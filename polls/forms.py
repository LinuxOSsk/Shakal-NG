# -*- coding: utf-8 -*-
from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.translation import gettext_lazy as _

from .models import Choice, Poll


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


ChoiceFormSet = formset_factory(ChoiceForm, formset=BaseChoiceFormSet, extra=10)
ChoiceFormSet.label = _('Choices')
ChoiceFormSet.hide_table_labels = True


class PollForm(forms.ModelForm):
	nested = []

	def __init__(self, data=None, *args, **kwargs):
		super(PollForm, self).__init__(data, *args, **kwargs)
		self.nested = [ChoiceFormSet(data)]

	def clean(self):
		cleaned_data = super(PollForm, self).clean()
		cleaned_data['choices'] = self.nested[0].clean()
		return cleaned_data

	class Meta:
		model = Poll
		exclude = ('approved', 'active_from', 'answer_count', 'content_type', 'object_id', 'slug')
		fields = ('question', 'checkbox')


class VoteForm(forms.Form):
	choice = forms.ModelMultipleChoiceField(queryset=Choice.objects.none())

	def __init__(self, poll, *args, **kwargs):
		super(VoteForm, self).__init__(*args, **kwargs)
		self.fields['choice'].queryset = poll.choices
