# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
