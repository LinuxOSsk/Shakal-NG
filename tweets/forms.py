# -*- coding: utf-8 -*-
from django import forms

from .models import Tweet
from web.middlewares.threadlocal import get_current_request


class TweetForm(forms.ModelForm):
	class Meta:
		model = Tweet
		fields = ('title', 'original_text', 'link_text', 'link_url')

	def save(self, commit=True):
		obj = super().save(commit=False)
		request = get_current_request()
		obj.author = request.user
		if commit:
			obj.save()
		return obj
