# -*- coding: utf-8 -*-
from django import forms

from .models import Attachment


class AttachmentForm(forms.ModelForm):
	class Meta:
		model = Attachment
		fields = ('attachment',)

	class Media:
		js = [
			'js/attachment-upload.js',
		]
