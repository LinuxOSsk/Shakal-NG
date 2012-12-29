# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.template import RequestContext
from datetime import datetime
from forms import TopicForm
from models import Section, Topic
from shakal.utils.generic import AddLoggedFormArgumentMixin, PreviewCreateView

def overview(request, section = None, page = 1):
	if section is not None:
		section = get_object_or_404(Section, slug = section)
		topics = Topic.topics.newest_topics(section = section.pk)
	else:
		topics = Topic.topics.newest_topics()
	print(section)

	context = {
		'forum': topics,
		'forum_section': section,
		'pagenum': page,
		'sections': Section.objects.all()
	}
	return TemplateResponse(request, "forum/topic_list.html", RequestContext(request, context))


def topic_detail(request, pk):
	topic = get_object_or_404(Topic, pk = pk)
	context = {
		'topic': topic
	}
	return TemplateResponse(request, "forum/topic_detail.html", RequestContext(request, context))


class TopicCreateView(AddLoggedFormArgumentMixin, PreviewCreateView):
	model = Topic
	template_name = 'forum/topic_create.html'
	form_class = TopicForm

	def form_valid(self, form):
		topic = form.save(commit = False)
		topic.time = datetime.now()
		if self.request.user.is_authenticated():
			if self.request.user.get_full_name():
				topic.username = self.request.user.get_full_name()
			else:
				topic.username = self.request.user.username
			topic.user = self.request.user
		return super(TopicCreateView, self).form_valid(form)
