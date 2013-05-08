# -*- coding: utf-8 -*-
from registration.backends.default import DefaultBackend
from forms import RegistrationFormUniqueEmail


class RegistrationBackend(DefaultBackend):
	def get_form_class(self, request):
		def form_class(*args, **kwargs):
			instance = RegistrationFormUniqueEmail(request, *args, **kwargs)
			return instance
		return form_class
