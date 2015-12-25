# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import Desktop


class DesktopCreateForm(forms.ModelForm):
	class Meta:
		model = Desktop
		fields = ('title', 'image', 'original_text')


class DesktopUpdateForm(forms.ModelForm):
	class Meta:
		model = Desktop
		fields = ('title', 'original_text')
