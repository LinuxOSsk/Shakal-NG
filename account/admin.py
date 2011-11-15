from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from shakal.account.models import UserProfile, UserProxy

class UserProfileInline(admin.StackedInline):
	model = UserProfile
	max_num = 1
	can_delete = False
	verbose_name = _('profile')
	verbose_name_plural = _('profiles')

class UserAdmin(AuthUserAdmin):
	inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProxy, UserAdmin)

