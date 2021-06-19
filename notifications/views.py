# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView

from notifications.models import Inbox


class List(LoginRequiredMixin, ListView):
	context_object_name = 'notifications'

	def get_queryset(self):
		return (Inbox.objects
			.user_messages(self.request.user)
			.filter(event__level__gt=0))[:99]


class Read(LoginRequiredMixin, DetailView):
	def get_queryset(self):
		return Inbox.objects.user_messages(self.request.user)

	def get(self, request, **kwargs):
		notification = self.get_object()
		event = notification.event
		Inbox.objects.filter(pk=notification.pk).update(readed=True)

		if event.linked_object:
			return HttpResponseRedirect(event.linked_object.get_absolute_url())
		if event.content_object:
			return HttpResponseRedirect(event.content_object.get_absolute_url())
		else:
			return HttpResponseRedirect(reverse("notifications:list"))
