# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.utils import timezone

from common_utils.generic import AddLoggedFormArgumentMixin, PreviewCreateView, DetailUserProtectedView, ListView
from forms import TopicForm
from models import Section, Topic


class TopicListView(ListView):
	queryset = Topic.topics.newest_topics()
	category = Section
	category_field = 'section'
	paginate_by = 50


class TopicDetailView(DetailUserProtectedView):
	superuser_perm = 'forum.delete_topic'
	queryset = Topic.objects.all().select_related("author", "section", "author__rating")
	unprivileged_queryset = Topic.objects.topics().select_related("author", "section", "author__rating")

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


class TopicCreateView(AddLoggedFormArgumentMixin, PreviewCreateView):
	model = Topic
	template_name = 'forum/topic_create.html'
	form_class = TopicForm

	def form_valid(self, form):
		ret = super(TopicCreateView, self).form_valid(form)
		if self.object:
			form.move_attachments(self.object)
		return ret
