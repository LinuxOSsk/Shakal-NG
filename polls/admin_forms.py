# -*- coding: utf-8 -*-
from django import forms

from .models import Poll
from common_utils.admin_widgets import AutosizedTextarea, DateTimeInput


class PollForm(forms.ModelForm):
	class Meta:
		model = Poll
		widgets = {
			'question': AutosizedTextarea(attrs={'class': 'input-xlarge'}),
			'slug': forms.TextInput(attrs={'class': 'input-xlarge'}),
			'active_from': DateTimeInput()
		}
