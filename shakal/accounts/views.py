# -*- coding: utf-8 -*-
from auth_remember import remember_user
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.views import login as login_view
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.safestring import mark_safe

def login(*args, **kwargs):
	return login_view(*args, **kwargs)

def profile(request, pk):
	user = get_object_or_404(User, pk = pk)
	profile = user.get_profile()
	user_table = (
		{ 'name': _('user name'), 'value': user.username },
		{ 'name': _('first name'), 'value': user.first_name },
		{ 'name': _('last name'), 'value': user.last_name },
		{ 'name': _('signature'), 'value': mark_safe(profile.signature) },
		{ 'name': _('info'), 'value': mark_safe(profile.info) },
		{ 'name': _('linux distribution'), 'value': profile.distribution },
		{ 'name': _('year of birth'), 'value': profile.year },
	)
	if profile.display_mail:
		email = user.email.replace('@', ' ' + ugettext('ROLLMOP') + ' ').replace('.', ' ' + ugettext('DOT') + ' ')
		user_table = user_table + ({ 'name': _('e-mail'), 'value': email}, )
	context = {
		'user_table': user_table
	}
	return TemplateResponse(request, "registration/profile.html", RequestContext(request, context))

def remember_user_handle(sender, request, user, **kwargs):
	if user.is_authenticated() and request.POST.get('remember_me', False):
		remember_user(request, user)

user_logged_in.connect(remember_user_handle, sender = User)
