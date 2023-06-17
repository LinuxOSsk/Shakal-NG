# -*- coding: utf-8 -*-
from django.views.generic import FormView

from .forms import NewsletterSubscriptionForm


class NewsletterSignupView(FormView):
	form_class = NewsletterSubscriptionForm
	template_name = 'newsletter/subscribe_form.html'
