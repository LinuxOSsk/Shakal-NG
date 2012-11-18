# -*- coding: utf-8 -*-

from django import forms


class ChangeTemplateForm(forms.Form):
	device = forms.CharField(required = False)
	template = forms.CharField(required = False)
	css = forms.CharField(required = False)


class ChangeTemplateHiddenForm(ChangeTemplateForm):
	def __init__(self, *args, **kwargs):
		super(ChangeTemplateHiddenForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget = forms.HiddenInput()
