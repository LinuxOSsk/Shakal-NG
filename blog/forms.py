# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms.models import modelformset_factory
from django.utils.timezone import now

from .models import Blog, Post
from attachment.fields import AttachmentFieldMultiple
from attachment.forms import AttachmentFormMixin
from attachment.models import Attachment


class BlogForm(forms.ModelForm):
	class Meta:
		model = Blog
		fields = ('title', 'original_description', 'original_sidebar',)


class PostForm(forms.ModelForm):
	pub_now = forms.BooleanField(label=u'Publikovať teraz', required=False)

	def __init__(self, *args, **kwargs):
		super(PostForm, self).__init__(*args, **kwargs)
		if self.instance and self.instance.published():
			del self.fields['pub_time']
			del self.fields['pub_now']
		else:
			self.fields['pub_time'].required = False

	def clean_pub_time(self):
		if 'pub_now' in self.data and self.data['pub_now']:
			return now()
		if not self.cleaned_data['pub_time']:
			raise forms.ValidationError("Nebol zadaný čas publikácie")
		if self.cleaned_data['pub_time'] < now():
			raise forms.ValidationError("Čas publikácie nesmie byť v minulosti")
		return self.cleaned_data['pub_time']

	class Meta:
		model = Post
		fields = ('title', 'original_perex', 'original_content', 'pub_time',)


AttachmentFormSetHiddable = modelformset_factory(Attachment, can_delete=True, extra=0, fields=('is_visible',))


class BlogAttachmentForm(AttachmentFormMixin, forms.Form):
	has_visibility = True
	formset = AttachmentFormSetHiddable
	attachment = AttachmentFieldMultiple(label='Príloha', required=False)
