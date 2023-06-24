# -*- coding: utf-8 -*-
from django import forms

from .models import NewsletterSubscription


class NewsletterSubscribeForm(forms.Form):
	email = NewsletterSubscription._meta.get_field('email').formfield()


class NewsletterUnsubscribeForm(forms.Form):
	email = forms.EmailField(
		label=NewsletterSubscription._meta.get_field('email').verbose_name.capitalize(),
		error_messages={'required': "Neplatný odkaz"}
	)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['email'].widget.attrs['disabled'] = 'disabled'
		if not self.data.get('email'):
			self.fields['email'].widget = forms.HiddenInput()
