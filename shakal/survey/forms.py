# -*- coding: utf-8 -*-

from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.translation import ugettext_lazy as _
from models import Answer, Survey

class BaseAnswerFormSet(BaseFormSet):
	def clean(self):
		if any(self.errors):
			return
		cleaned_data = []
		for i in range(0, self.total_form_count()):
			form = self.forms[i]
			if 'answer' in form.cleaned_data and form.cleaned_data['answer']:
				cleaned_data.append(form.cleaned_data)
		if len(cleaned_data) < 2:
			raise forms.ValidationError(_("Minimum 2 answers are required"))
		return cleaned_data

class AnswerForm(forms.ModelForm):
	class Meta:
		model = Answer
		exclude = ('survey', 'votes', )

AnswerFormSet = formset_factory(AnswerForm, formset = BaseAnswerFormSet, extra = 10)
AnswerFormSet.label = _('Answers')
AnswerFormSet.hide_table_labels = True

class SurveyForm(forms.ModelForm):
	nested = []

	def __init__(self, data = None, *args, **kwargs):
		super(SurveyForm, self).__init__(data, *args, **kwargs)
		self.nested = [AnswerFormSet(data)]

	def clean(self):
		cleaned_data = super(SurveyForm, self).clean()
		cleaned_data['answers'] = self.nested[0].clean()
		return cleaned_data

	class Meta:
		model = Survey
		exclude = ('approved', 'active_from', 'answer_count', 'content_type', 'object_id', 'slug')
		fields = ('question', 'checkbox')
