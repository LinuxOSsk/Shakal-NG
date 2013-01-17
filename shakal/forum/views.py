# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
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

	context = {
		'forum': topics,
		'forum_section': section,
		'pagenum': page,
		'sections': Section.objects.all()
	}
	return TemplateResponse(request, "forum/topic_list.html", RequestContext(request, context))


def topic_detail(request, pk):
	delete_perm = request.user.has_perm('forum.delete_topic')
	if delete_perm:
		topic = get_object_or_404(Topic.objects.all(), pk = pk)
	else:
		topic = get_object_or_404(Topic.objects.topics(), pk = pk)
	topic.resolved_perm = request.user.has_perm('forum.change_topic') or (topic.author and topic.author == request.user)
	topic.delete_perm = delete_perm

	if request.GET:
		if 'resolved' in request.GET and topic.resolved_perm:
			topic.is_resolved = bool(request.GET['resolved'])
			topic.save()
			return HttpResponseRedirect(topic.get_absolute_url())
		if 'removed' in request.GET and topic.delete_perm:
			topic.is_removed = bool(request.GET['removed'])
			topic.save()
			return HttpResponseRedirect(topic.get_absolute_url())

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
		topic.created = datetime.now()
		if self.request.user.is_authenticated():
			if self.request.user.get_full_name():
				topic.authors_name = self.request.user.get_full_name()
			else:
				topic.authors_name = self.request.user.username
			topic.author = self.request.user
		topic.updated = topic.created
		return super(TopicCreateView, self).form_valid(form)
