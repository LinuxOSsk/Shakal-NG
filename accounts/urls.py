# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from forms import RegistrationFormUniqueEmail

class Pattenrs(object):
	def __init__(self):
		self.app_name = 'accounts'
		self.name = 'accounts'
		self.register_context = {
			'form_class': RegistrationFormUniqueEmail,
			'backend': 'registration.backends.default.DefaultBackend'}

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^register/$', 'registration.views.register', self.register_context, name='registration_register'),
			url(r'^', include('registration.backends.default.urls')),
		)
		return urlpatterns


urlpatterns = Pattenrs().urls
