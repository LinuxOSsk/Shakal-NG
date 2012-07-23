# -*- coding: utf-8 -*-
from auth_remember import remember_user
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.views import login as login_view

def login(*args, **kwargs):
	return login_view(*args, **kwargs)

def remember_user_handle(sender, request, user, **kwargs):
	if user.is_authenticated() and request.POST.get('remember_me', False):
		remember_user(request, user)

user_logged_in.connect(remember_user_handle, sender = User)
