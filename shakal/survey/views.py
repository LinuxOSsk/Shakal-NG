# -*- coding: utf-8 -*-

from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect

@require_POST
def post(request, pk):
	return HttpResponseRedirect(request.POST['next'])
