# -*- coding: utf-8 -*-
from django.views.generic import CreateView

from .forms import NewsletterForm


class NewsletterSignupView(CreateView):
	form_class = NewsletterForm
