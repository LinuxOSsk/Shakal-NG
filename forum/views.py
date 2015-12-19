# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Count
from django.http.response import HttpResponseRedirect
from django.views.generic import DetailView

from .forms import TopicForm
from .models import Topic, Section
from common_utils.generic import ListView, PreviewCreateView


class TopicListView(ListView):
	queryset = Topic.topics.newest_topics()
	category_model = Section
	category_field = 'section'
	paginate_by = 50


class TopicDetailView(DetailView):
	queryset = Topic.objects.all().select_related("author", "section", "author__rating").annotate(attachment_count=Count('attachments'))

	def get_object(self, queryset = None):
		topic = super(TopicDetailView, self).get_object(queryset)
		topic.resolved_perm = self.request.user.has_perm('forum.change_topic') or (topic.author and topic.author == self.request.user)
		topic.delete_perm = self.request.user.has_perm('forum.delete_topic')
		return topic

	def get(self, request, *args, **kwargs):
		if 'resolved' in request.GET or 'removed' in request.GET:
			topic = self.get_object()
			if 'resolved' in request.GET and topic.resolved_perm:
				topic.is_resolved = bool(request.GET['resolved'])
				topic.save()
				return HttpResponseRedirect(topic.get_absolute_url())
			if 'removed' in request.GET and topic.delete_perm:
				topic.is_removed = bool(request.GET['removed'])
				topic.save()
				return HttpResponseRedirect(topic.get_absolute_url())
		return super(TopicDetailView, self).get(request, *args, **kwargs)


class TopicCreateView(PreviewCreateView):
	model = Topic
	form_class = TopicForm

	def form_valid(self, form):
		ret = super(TopicCreateView, self).form_valid(form)
		if self.object:
			form.move_attachments(self.object)
		return ret
