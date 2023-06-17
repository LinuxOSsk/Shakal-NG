# -*- coding: utf-8 -*-
from django.forms import ModelForm

from .models import NewsletterSubscription


class NewsletterSubscriptionForm(ModelForm):
	class Meta:
		model = NewsletterSubscription
		fields = ['email']
