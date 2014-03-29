# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from accounts.forms import UserCreationForm, UserChangeForm
from accounts.models import User
from admin_actions.views import AdminActionsMixin


class UserAdmin(AdminActionsMixin, AuthUserAdmin):
	add_form = UserCreationForm
	form = UserChangeForm
	ordering = ('-id', )
	list_display = ['username', 'email', 'get_full_name', 'get_status']

	def get_status(self, obj):
		cls = 'important'
		status_text = _('inactive')
		if obj.is_active:
			if obj.is_superuser:
				cls = 'inverse'
				status_text = _('super user')
			elif obj.is_staff:
				cls = 'success'
				status_text = _('staff')
			else:
				cls = 'info'
				status_text = _('active')

		return format_html(u'<span class="label label-{0}">{1}</span>', cls, unicode(status_text))
	get_status.short_description = _("status")
	get_status.allow_tags = True

	def get_changelist_actions(self, obj):
		if obj.is_active:
			return (('set_inactive', {'label': _('Block user'), 'class': 'btn btn-danger'}),)
		else:
			return (('set_active', {'label': _('Unblock user'), 'class': 'btn btn-success'}),)

	def set_inactive(self, request, **kwargs): #pylint: disable=W0613
		request.POST['is_active'] = ''

	def set_active(self, request, **kwargs): #pylint: disable=W0613
		request.POST['is_active'] = '1'

admin.site.register(User, UserAdmin)
