# -*- coding: utf-8 -*-
from django import forms
from django.utils.timezone import now

from .models import Blog, Post
from common_utils import get_meta
from rich_editor.forms import RichOriginalField


class BlogForm(forms.ModelForm):
	original_description = RichOriginalField(get_meta(Blog).get_field('original_description').parsers, label=u'Popis', max_length=1000) #pylint: disable=W0212
	original_sidebar = RichOriginalField(get_meta(Blog).get_field('original_sidebar').parsers, label=u'Bočný panel', max_length=1000) #pylint: disable=W0212
	class Meta:
		model = Blog
		exclude = ('author', 'slug')


class PostForm(forms.ModelForm):
	original_perex = RichOriginalField(get_meta(Post).get_field('original_perex').parsers, label=u'Perex', max_length=1000) #pylint: disable=W0212
	original_content = RichOriginalField(get_meta(Post).get_field('original_content').parsers, label=u'Obsah', max_length=100000) #pylint: disable=W0212
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
		exclude = ('blog', 'slug', 'linux')
