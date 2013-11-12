# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.utils.translation import ugettext_lazy as _

from accounts import views as accounts_views
from forms import AuthenticationRememberForm


class Patterns(object):
	def __init__(self):
		self.app_name = 'accounts'
		self.name = 'accounts'
		self.register_context = {'backend': 'accounts.backend.RegistrationBackend'}

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'', include('accounts.registration_backend.urls')),
			url(r'^$', accounts_views.user_zone, name = 'auth_user_zone'),
			url(r'^(?P<pk>\d+)/$', accounts_views.profile, name = 'auth_profile'),
			url(_(r'^me/$'), accounts_views.my_profile, name = 'auth_my_profile'),
			url(_(r'^me/edit/$'), accounts_views.my_profile_edit, name = 'auth_my_profile_edit'),
			url(_(r'^login/$'), accounts_views.login, {'template_name': 'registration/login.html', 'authentication_form': AuthenticationRememberForm}, name = 'auth_login'),
			url(_(r'^email/change/$'), accounts_views.email_change, name = 'auth_email_change'),
			url(_(r'^email/change/done/$'), accounts_views.email_change_done, name = 'auth_email_change_done'),
			url(_(r'^email/change/activate/(?P<email>.*)/$'), accounts_views.email_change_activate, name = 'auth_email_change_activate'),
		)
		return urlpatterns


urlpatterns = Patterns().urls
