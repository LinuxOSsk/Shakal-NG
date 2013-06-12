# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from notifications.models import Inbox


@login_required
def list(request):
	context = {
		'notifications': Inbox.objects.user_messages(request.user).filter(event__level__gt = 0)[:99]
	}
	return TemplateResponse(request, "notifications/list.html", context)


@login_required
def read(request, pk):
	notification = get_object_or_404(Inbox.objects.user_messages(request.user), pk = pk)
	event = notification.event
	notification.readed = True
	notification.save()

	if event.content_object:
		return HttpResponseRedirect(event.content_object.get_absolute_url())
	else:
		return HttpResponseRedirect(reverse("notifications:list"))
