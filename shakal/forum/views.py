# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.template import RequestContext
from models import Topic

def topic_detail(request, pk):
	topic = get_object_or_404(Topic, pk = pk)
	context = {
		'topic': topic
	}
	return TemplateResponse(request, "forum/topic_detail.html", RequestContext(request, context))

