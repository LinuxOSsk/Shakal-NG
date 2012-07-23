# -*- coding: utf-8 -*-
from auth_remember import remember_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.views import login as login_view
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.safestring import mark_safe
from django.views.generic import UpdateView
from forms import ProfileEditForm
from models import UserProfile

def login(*args, **kwargs):
	return login_view(*args, **kwargs)


def profile(request, pk):
	user = get_object_or_404(User, pk = pk)
	profile = user.get_profile()
	user_table = (
		{ 'name': _('user name'), 'value': user.username },
		{ 'name': _('first name'), 'value': user.first_name },
		{ 'name': _('last name'), 'value': user.last_name },
		{ 'name': _('signature'), 'value': mark_safe(profile.signature) },
		{ 'name': _('info'), 'value': mark_safe(profile.info) },
		{ 'name': _('linux distribution'), 'value': profile.distribution },
		{ 'name': _('year of birth'), 'value': profile.year },
	)
	if profile.display_mail:
		email = user.email.replace('@', ' ' + ugettext('ROLLMOP') + ' ').replace('.', ' ' + ugettext('DOT') + ' ')
		user_table = user_table + ({ 'name': _('e-mail'), 'value': email}, )
	context = {
		'user_table': user_table,
		'is_my_profile': request.user == user,
	}
	return TemplateResponse(request, "registration/profile.html", RequestContext(request, context))


@login_required
def my_profile(request):
	return profile(request, request.user.pk)


@login_required
def my_profile_edit(request):
	return profile_edit(request, request.user.pk)


def profile_edit(request, pk):
	user = get_object_or_404(UserProfile, user = pk)
	return ProfileEditView.as_view()(request, pk = user.pk)


class ProfileEditView(UpdateView):
	form_class = ProfileEditForm
	model = UserProfile
	template_name = 'registration/profile_change.html'

	def get_success_url(self):
		return reverse('auth_my_profile')


def remember_user_handle(sender, request, user, **kwargs):
	if user.is_authenticated() and request.POST.get('remember_me', False):
		remember_user(request, user)

user_logged_in.connect(remember_user_handle, sender = User)
