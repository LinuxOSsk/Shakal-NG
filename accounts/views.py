# -*- coding: utf-8 -*-
from datetime import datetime
from time import mktime

from auth_remember import remember_user
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.models import get_current_site
from django.core import signing
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext
from django.views.generic import RedirectView, UpdateView

from .forms import ProfileEditForm, EmailChangeForm


def profile(request, pk):
	user = get_object_or_404(get_user_model(), pk=pk)
	user_table = (
		{'name': _('user name'), 'value': user.username, 'class': 'nickname'},
		{'name': _('full name'), 'value': (user.first_name + ' ' + user.last_name).strip(), 'class': 'fn'},
		{'name': _('signature'), 'value': mark_safe(user.signature), 'class': ''},
		{'name': _('linux distribution'), 'value': user.distribution, 'class': 'note'},
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
	return HttpResponseRedirect(reverse("auth_profile", args=[request.user.pk]))


def sign_email_change_link(user_pk, time, email):
	signer = signing.Signer()
	signed = signer.sign(str(user_pk) + '.' + str(time) + '.' + email)
	return reverse('auth_email_change_activate', args=(signed,))


@login_required
def email_change(request):
	form = EmailChangeForm(request.POST or None, initial={'email': request.user.email})
	if form.is_valid():
		email = form.cleaned_data['email']
		signed = sign_email_change_link(request.user.pk, int(mktime(timezone.now().timetuple())), email)
		context_data = {
			'email': signed,
			'site': get_current_site(request),
			'activate_link': request.build_absolute_uri(signed),
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
		user = get_user_model().objects.get(pk=int(user_id))
		if user != request.user:
			raise ValueError
		time = timezone.make_aware(datetime.utcfromtimestamp(int(timestamp)), timezone=timezone.utc)
		if ((timezone.now() - time).days) > 14:
			raise UserInputError(_("Link expired."))
		if get_user_model().objects.filter(email=email).exclude(pk=user.pk).count() > 0:
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
	user = get_object_or_404(get_user_model(), pk=pk)
	return ProfileEditView.as_view()(request, pk=user.pk)


class ProfileEditView(UpdateView):
	form_class = ProfileEditForm
	model = get_user_model()
	template_name = 'registration/profile_change.html'

	def get_success_url(self):
		return reverse('auth_my_profile')


user_zone = login_required(RedirectView.as_view(url=reverse_lazy('auth_my_profile')))


def remember_user_handle(sender, request, user, **kwargs): #pylint: disable=W0613
	if user.is_authenticated() and request.POST.get('remember_me', False):
		remember_user(request, user)

user_logged_in.connect(remember_user_handle, sender=get_user_model())
