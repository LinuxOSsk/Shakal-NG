# -*- coding: utf-8 -*-
from django import forms

from .models import NewsletterSubscription


class NewsletterSubscribeForm(forms.Form):
	email = NewsletterSubscription._meta.get_field('email').formfield()


class NewsletterUnsubscribeForm(forms.Form):
	email = forms.HiddenInput()
	token = forms.HiddenInput()
