# -*- coding: utf-8 -*-

from django.views.generic import CreateView

class AddLoggedFormArgumentMixin(object):
	def get_form(self, form_class):
		return form_class(logged = self.request.user.is_authenticated(), **self.get_form_kwargs())
