# -*- coding: utf-8 -*-

from django.template.response import TemplateResponse

def home(request):
	return TemplateResponse(request, "home.html", {})
