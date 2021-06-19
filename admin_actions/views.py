# -*- coding: utf-8 -*-
from django.contrib.admin.utils import unquote
from django.http import HttpResponse


class AdminActionsMixin(object):
	def get_changelist_actions(self, obj):
		return self.changelist_actions if obj else ()

	def change_view(self, request, object_id, form_url='', extra_context=None):
		obj = self.get_object(request, unquote(object_id))
		changelist_actions = self.get_changelist_actions(obj)

		for action in changelist_actions:
			if '_' + action[0] in request.POST:
				request.POST['_continue'] = True
				action_method = getattr(self, action[0])
				response = action_method(request=request, obj=obj, form_url=form_url, extra_context=extra_context)
				if isinstance(response, HttpResponse):
					return response

		extra_context = extra_context or {}
		extra_context['changelist_actions'] = [{'action': a[0], 'options': a[1]} for a in changelist_actions]
		return super(AdminActionsMixin, self).change_view(request, object_id, form_url, extra_context)
