# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.utils.translation import ugettext_lazy as _
from forms import RegistrationFormUniqueEmail, AuthenticationRememberForm
from shakal.accounts import views as accounts_views

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
			url(r'^', include('registration.backends.default.urls')),
			url(r'^$', accounts_views.user_zone, name = 'auth_user_zone'),
			url(r'^(?P<pk>[0-9]+)/$', accounts_views.profile, name = 'auth_profile'),
			url(_(r'^me/$'), accounts_views.my_profile, name = 'auth_my_profile'),
			url(_(r'^me/edit/$'), accounts_views.my_profile_edit, name = 'auth_my_profile_edit'),
			url(_(r'^register/$'), 'registration.views.register', self.register_context, name = 'registration_register'),
			url(_(r'^login/$'), accounts_views.login, {'template_name' : 'registration/login.html', 'authentication_form': AuthenticationRememberForm}, name = 'auth_login'),
		)
		return urlpatterns


urlpatterns = Pattenrs().urls
