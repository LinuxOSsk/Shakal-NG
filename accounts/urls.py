# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.utils.translation import ugettext_lazy as _


class Patterns(object):
	def __init__(self):
		self.app_name = 'accounts'
		self.name = 'accounts'

	@property
	def urls(self):
		pat = patterns('accounts.views',
			url(r'^$', 'UserZone', name='account_user_zone'),
			url(r'^(?P<pk>\d+)/$', 'Profile', name='account_profile'),
			url(_(r'^me/$'), 'MyProfile', name='account_my_profile'),
			url(_(r'^me/edit/$'), 'MyProfileEdit', name='account_my_profile_edit'),
			url(r'', include('allauth.urls')),
		)
		return pat


urlpatterns = Patterns().urls
