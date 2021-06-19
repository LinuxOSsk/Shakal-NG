# -*- coding: utf-8 -*-
from django import forms


class ChangeTemplateForm(forms.Form):
	template = forms.CharField(required=False)
	css = forms.CharField(required=False)
	settings = forms.CharField(required=False)
	next = forms.CharField(required=False)


class ChangeTemplateHiddenForm(ChangeTemplateForm):
	def __init__(self, *args, **kwargs):
		super(ChangeTemplateHiddenForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget = forms.HiddenInput()
