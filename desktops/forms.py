# -*- coding: utf-8 -*-
from django import forms

from .models import Desktop
from attachment.fields import AttachmentImageField, AttachmentWidget


class DesktopCreateForm(forms.ModelForm):
	image = AttachmentImageField(
		label='Desktop',
		widget=AttachmentWidget(attrs={
			'max_size': 1024 * 1024 * 2
		})
	)

	class Meta:
		model = Desktop
		fields = ('title', 'image', 'original_text')


class DesktopUpdateForm(forms.ModelForm):
	class Meta:
		model = Desktop
		fields = ('title', 'original_text')
