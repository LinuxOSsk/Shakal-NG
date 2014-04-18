# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from registration import signals
from registration.backends.default.views import RegistrationView as DefaultRegistrationView
from registration.models import RegistrationProfile

from accounts.models import User


class RegistrationView(DefaultRegistrationView):
	def register(self, request, **cleaned_data):
		username, email, password = cleaned_data['username'], cleaned_data['email'], cleaned_data['password1']
		site = Site.objects.get_current()

		new_user = User.objects.create_user(username, email, password)
		for key, value in cleaned_data.iteritems():
			if hasattr(new_user, key) and key != "password":
				setattr(new_user, key, value)
		new_user.is_active = False
		new_user.save()

		registration_profile = RegistrationProfile.objects.create_profile(new_user)
		registration_profile.send_activation_email(site)

		signals.user_registered.send(sender=self.__class__, user=new_user, request=request)
		return new_user

	def dispatch(self, request, *args, **kwargs):
		setattr(self, 'request', request)
		return super(RegistrationView, self).dispatch(request, *args ,**kwargs)

	def get_form(self, form_class):
		form = form_class(**self.get_form_kwargs())
		return form

	def get_form_kwargs(self, request=None, form_class=None):
		kwargs = super(RegistrationView, self).get_form_kwargs(request, form_class)
		kwargs['request'] = getattr(self, 'request', None)
		return kwargs
