# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect

def profile_redirect(request, pk):
	return HttpResponsePermanentRedirect(reverse('auth_profile', kwargs = {'pk': pk}))
