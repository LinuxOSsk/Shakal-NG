# -*- coding: utf-8 -*-
from django.contrib import messages
from django.http.response import HttpResponse, Http404
from django.utils import timezone
from django.views.generic import FormView, View

from .api import render_weekly
from .forms import NewsletterSubscriptionForm
from .models import NewsletterSubscription
from common_utils.generic import NextRedirectMixin


class NewsletterSubscribeView(NextRedirectMixin, FormView):
	form_class = NewsletterSubscriptionForm
	template_name = 'newsletter/subscribe_form.html'
	next_page = 'home'

	def form_valid(self, form):
		email = form.cleaned_data['email']
		NewsletterSubscription.objects.update_or_create(
			email=email,
			defaults={'updated': timezone.now()}
		)
		messages.success(self.request, f"E-mail „{email}“ bol zaregistrovaný pre odber noviniek")
		return super().form_valid(form)


class WeeklyNewsletterPreview(View):
	def get(self, request, **kwargs):
		rendered = render_weekly(self.kwargs['date'])
		if not rendered:
			raise Http404()
		if kwargs['format'] == 'txt':
			return self.render_txt(rendered)
		else:
			return self.render_html(rendered)

	def render_txt(self, rendered):
		return HttpResponse(
			rendered['title'] + '\n\n' + rendered['txt_data'],
			content_type='text/plain; charset=utf-8'
		)

	def render_html(self, rendered):
		return HttpResponse(rendered['html_data'])
