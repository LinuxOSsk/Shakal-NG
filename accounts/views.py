# -*- coding: utf-8 -*-
from datetime import datetime
from time import mktime

from auth_remember import remember_user
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.views import login as login_view
from django.contrib.sites.models import get_current_site
from django.core import signing
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext
from django.views.generic import RedirectView, UpdateView

from forms import ProfileEditForm, EmailChangeForm


def login(*args, **kwargs):
	return login_view(*args, **kwargs)


def profile(request, pk):
	user = get_object_or_404(get_user_model(), pk = pk)
	user_table = (
		{'name': _('user name'), 'value': user.username},
		{'name': _('first name'), 'value': user.first_name},
		{'name': _('last name'), 'value': user.last_name},
		{'name': _('signature'), 'value': mark_safe(user.signature)},
		{'name': _('linux distribution'), 'value': user.distribution},
		{'name': _('year of birth'), 'value': user.year},
	)
	if user.display_mail:
		email = user.email.replace('@', ' ' + ugettext('ROLLMOP') + ' ').replace('.', ' ' + ugettext('DOT') + ' ')
		user_table = user_table + ({'name': _('e-mail'), 'value': email}, )
	context = {
		'user_table': user_table,
		'user_profile': user,
		'is_my_profile': request.user == user,
	}
	return TemplateResponse(request, "registration/profile.html", RequestContext(request, context))


@login_required
def my_profile(request):
	return profile(request, request.user.pk)


@login_required
def email_change(request):
	if request.method == 'GET':
		form = EmailChangeForm(initial = {'email': request.user.email})
	else:
		form = EmailChangeForm(request.POST)
		if form.is_valid():
			if form.cleaned_data['email'] == request.user.email:
				return HttpResponseRedirect(reverse('auth_my_profile'))
			else:
				signer = signing.Signer()
				email = form.cleaned_data['email']
				signed = signer.sign(str(request.user.pk) + '.' + str(int(mktime(datetime.now().timetuple()))) + '.' + email)
				context_data = {
					'email': signed,
					'site': get_current_site(request)
				}
				context = RequestContext(request, context_data)
				email_subject = render_to_string("registration/email_change_subject.txt", context).rstrip("\n")
				email_body = render_to_string("registration/email_change.txt", context)
				send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [email])
				return HttpResponseRedirect(reverse('auth_email_change_done'))

	return TemplateResponse(request, "registration/email_change_form.html", {'form': form})


@login_required
def email_change_done(request):
	return TemplateResponse(request, "registration/email_change_done.html")


@login_required
def email_change_activate(request, email):
	class UserInputError(ValueError):
		pass
	context = {
		'validlink': True,
	}
	try:
		signer = signing.Signer()
		email_data = signer.unsign(email)
		user_id, timestamp, email = email_data.split('.', 2)
		user = get_user_model().objects.get(pk = int(user_id))
		if user != request.user:
			raise ValueError
		time = datetime.fromtimestamp(int(timestamp))
		if ((datetime.now() - time).days) > 14:
			raise UserInputError(_("Link expired."))
		if get_user_model().objects.filter(email = email).exclude(pk = user.pk).count() > 0:
			raise UserInputError(_("E-mail address is already in use."))
		user.email = email
		user.save()
	except UserInputError as e:
		context['validlink'] = False
		context['error_message'] = e.message
	except (signing.BadSignature, ValueError, get_user_model().DoesNotExist) as e:
		context['validlink'] = False
	return TemplateResponse(request, "registration/email_change_complete.html", context)


@login_required
def my_profile_edit(request):
	return profile_edit(request, request.user.pk)


def profile_edit(request, pk):
	user = get_object_or_404(get_user_model(), pk = pk)
	return ProfileEditView.as_view()(request, pk = user.pk)


class ProfileEditView(UpdateView):
	form_class = ProfileEditForm
	model = get_user_model()
	template_name = 'registration/profile_change.html'

	def get_success_url(self):
		return reverse('auth_my_profile')


user_zone = login_required(RedirectView.as_view(url = reverse_lazy('auth_my_profile')))


def remember_user_handle(sender, request, user, **kwargs):
	if user.is_authenticated() and request.POST.get('remember_me', False):
		remember_user(request, user)

user_logged_in.connect(remember_user_handle, sender = get_user_model())
