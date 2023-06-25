# -*- coding: utf-8 -*-
from typing import Optional

from django.contrib import messages
from django.http import QueryDict
from django.http.response import HttpResponse, Http404
from django.utils import timezone
from django.views.generic import FormView, View

from .api import render_weekly, unsign_email
from .forms import NewsletterSubscribeForm, NewsletterUnsubscribeForm
from .models import NewsletterSubscription
from common_utils.generic import NextRedirectMixin


class NewsletterSubscribeView(NextRedirectMixin, FormView):
	form_class = NewsletterSubscribeForm
	template_name = 'newsletter/subscribe_form.html'
	next_page = 'home'

	def get_initial(self):
		initial = super().get_initial()
		email = self.request.GET.get('email')
		if email is not None:
			initial.setdefault('email', email)
		return initial

	def form_valid(self, form):
		email = form.cleaned_data['email']
		NewsletterSubscription.objects.update_or_create(
			email=email,
			defaults={'updated': timezone.now()}
		)
		messages.success(self.request, f"E-mail „{email}“ bol zaregistrovaný pre odber noviniek")
		return super().form_valid(form)


class NewsletterUnsubscribeView(NextRedirectMixin, FormView):
	form_class = NewsletterUnsubscribeForm
	template_name = 'newsletter/unsubscribe_form.html'
	next_page = 'home'

	def decode_email(self) -> Optional[str]:
		"""
		Returns e-mail if can be decoded from link or None if it's bad link
		"""
		return unsign_email(self.kwargs['token'])

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		q = QueryDict('', mutable=True)
		q.update({'email': self.decode_email()})
		kwargs['data'] = q
		return kwargs

	def dispatch(self, request, *args, **kwargs):
		self.email = self.decode_email()
		return super().dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		email = self.decode_email()
		NewsletterSubscription.objects.filter(email=self.email).delete()
		messages.success(self.request, f"E-mail „{email}“ bol vyradený z odberu noviniek")
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
