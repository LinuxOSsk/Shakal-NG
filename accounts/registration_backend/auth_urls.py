# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns
from django.contrib.auth import views as auth_views
from accounts.registration_backend.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm


urlpatterns = patterns('',
	url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html', 'authentication_form': AuthenticationForm}, name='auth_login'),
	url(r'^logout/$', auth_views.logout, {'template_name': 'registration/logout.html'}, name='auth_logout'),
	url(r'^password/change/$', auth_views.password_change, {'password_change_form': PasswordChangeForm}, name='password_change'),
	url(r'^password/change/done/$', auth_views.password_change_done, name='password_change_done'),
	url(r'^password/reset/$', auth_views.password_reset, {'password_reset_form': PasswordResetForm}, name='password_reset'),
	url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, {'set_password_form': SetPasswordForm}, name='password_reset_confirm'),
	url(r'^password/reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
	url(r'^password/reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
)
