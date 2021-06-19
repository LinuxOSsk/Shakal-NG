# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseRedirect
from django.views.generic import CreateView

from .forms import NoteForm
from .models import Note


class NoteCreateBase(CreateView):
	model = Note
	form_class = NoteForm

	def get_content_object(self):
		raise NotImplementedError()

	def form_valid(self, form):
		content_object = self.content_object
		content_type = ContentType.objects.get_for_model(content_object.__class__)
		object_id = content_object.pk
		note = form.save(commit=False)
		note.content_type = content_type
		note.object_id = object_id
		note.save()
		return HttpResponseRedirect(self.get_success_url())

	def dispatch(self, request, *args, **kwargs):
		self.content_object = self.get_content_object()
		return super(NoteCreateBase, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		ctx = super(NoteCreateBase, self).get_context_data(**kwargs)
		ctx['content_object'] = self.content_object
		return  ctx

	def get_success_url(self):
		return self.content_object.get_absolute_url()
