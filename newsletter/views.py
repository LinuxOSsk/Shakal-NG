# -*- coding: utf-8 -*-
from django.contrib import messages
from django.views.generic import FormView

from .forms import NewsletterSubscriptionForm
from .models import NewsletterSubscription
from common_utils.generic import NextRedirectMixin


class NewsletterSubscribeView(NextRedirectMixin, FormView):
	form_class = NewsletterSubscriptionForm
	template_name = 'newsletter/subscribe_form.html'
	next_page = 'home'

	def form_valid(self, form):
		email = form.cleaned_data['email']
		NewsletterSubscription.objects.get_or_create(email=email)
		messages.success(self.request, f"E-mail „{email}“ bol zaregistrovaný pre odber noviniek")
		return super().form_valid(form)
