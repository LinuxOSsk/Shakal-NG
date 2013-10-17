# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from accounts.forms import UserAdminForm, UserAdminAddForm
from accounts.models import User


class UserAdmin(AuthUserAdmin):
	form = UserAdminForm
	add_form = UserAdminAddForm
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


admin.site.register(User, UserAdmin)
