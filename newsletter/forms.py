# -*- coding: utf-8 -*-
from django.forms import Form

from .models import NewsletterSubscription


class NewsletterSubscriptionForm(Form):
	email = NewsletterSubscription._meta.get_field('email').formfield()
