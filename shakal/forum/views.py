# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.template import RequestContext
from models import Section, Topic


def overview(request, section = None, page = 1):
	topics = Topic.objects
	if section is not None:
		section = get_object_or_404(Section, slug = section)
		topics = topics.filter(section = section)

	context = {
		'forum': topics.order_by('-pk').all(),
		'section': section,
		'pagenum': page,
		'sections': Section.objects.all
	}
	return TemplateResponse(request, "forum/topic_list.html", RequestContext(request, context))


def topic_detail(request, pk):
	topic = get_object_or_404(Topic, pk = pk)
	context = {
		'topic': topic
	}
	return TemplateResponse(request, "forum/topic_detail.html", RequestContext(request, context))

