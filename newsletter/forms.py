# -*- coding: utf-8 -*-
from django import forms
from django.core.validators import ValidationError

from .api import unsign_email
from .models import NewsletterSubscription


class NewsletterSubscribeForm(forms.Form):
	email = NewsletterSubscription._meta.get_field('email').formfield()


class NewsletterUnsubscribeForm(forms.Form):
	email = forms.HiddenInput()

	def clean(self):
		cleaned_data = super().clean()
		email = unsign_email(cleaned_data.get('email', ''))
		if email is None:
			raise ValidationError("Neplatný odkaz")
		cleaned_data['email'] = email
		return cleaned_data


# TODO: unsubscribe without link using e-mail form
