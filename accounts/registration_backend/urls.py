# -*- coding: utf-8 -*-
from django.conf.urls import url, include, patterns
from django.views.generic.base import TemplateView
from registration.backends.default.views import ActivationView

from accounts.registration_backend.forms import UserRegistrationForm
from accounts.registration_backend.views import RegistrationView


urlpatterns = patterns('',
	url(r'^activate/complete/$', TemplateView.as_view(template_name='registration/activation_complete.html'), name='registration_activation_complete'),
	url(r'^activate/(?P<activation_key>\w+)/$', ActivationView.as_view(), name='registration_activate'),
	url(r'^register/$', RegistrationView.as_view(form_class=UserRegistrationForm), name='registration_register'),
	url(r'^register/complete/$', TemplateView.as_view(template_name='registration/registration_complete.html'), name='registration_complete'),
	url(r'^register/closed/$', TemplateView.as_view(template_name='registration/registration_closed.html'), name='registration_disallowed'),
	url(r'', include('accounts.registration_backend.auth_urls')),
)
