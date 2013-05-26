# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from accounts.forms import LessRestrictiveUserChangeForm, LessRestrictiveUserCreationForm
from accounts.models import User


class UserAdmin(AuthUserAdmin):
	form = LessRestrictiveUserChangeForm
	add_form = LessRestrictiveUserCreationForm
	ordering = ('-id', )


admin.site.register(User, UserAdmin)
