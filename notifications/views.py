# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from notifications.models import Inbox


@login_required
def read(request):
	context = {
		'notifications': Inbox.objects.user_messages(request.user)
	}
	return TemplateResponse(request, "notifications/read.html", context)
