# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from accounts.admin_forms import UserCreationForm, UserChangeForm
from accounts.models import User
from admin_actions.views import AdminActionsMixin
from hijack.contrib.admin import HijackUserAdminMixin


class UserAdmin(HijackUserAdminMixin, AdminActionsMixin, AuthUserAdmin):
	add_form = UserCreationForm
	form = UserChangeForm
	ordering = ('-id', )
	list_display = ['username', 'email', 'get_full_name', 'get_status']
	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		('Osobné údaje', {'fields': ('first_name', 'last_name',)}),
		('Práva', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		('Dôležité dátumy', {'fields': ('last_login', 'date_joined', 'year')}),
		('Kontaktné údaje', {'fields': ('email', 'jabber', 'url', 'display_mail', 'geoposition')}),
		('Ďalšie údaje', {'fields': ('distribution', 'original_info', 'avatar',)}),
		('Rozšírené', {'classes': ('collapse',), 'fields': ('settings',)}),
	)

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

		return render_to_string('admin/partials/label.html', {'cls': cls, 'text': status_text})
	get_status.short_description = _("status")
	get_status.allow_tags = True

	def get_changelist_actions(self, obj):
		if not obj:
			return ()
		if obj.is_active:
			return (('set_inactive', {'label': _('Block user'), 'class': 'btn btn-danger'}),)
		else:
			return (('set_active', {'label': _('Unblock user'), 'class': 'btn btn-success'}),)

	def set_inactive(self, request, **kwargs):
		request.POST['is_active'] = ''

	def set_active(self, request, **kwargs):
		request.POST['is_active'] = '1'

	def get_hijack_user(self, obj):
		return obj


admin.site.register(User, UserAdmin)
