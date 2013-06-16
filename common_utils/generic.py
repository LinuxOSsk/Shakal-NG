# -*- coding: utf-8 -*-

from django.db.models import Q
from django.views.generic import CreateView, UpdateView, DetailView
from hitcount.models import HitCountField


class AddLoggedFormArgumentMixin(object):
	def get_form(self, form_class):
		return form_class(logged = self.request.user.is_authenticated(), request = self.request, **self.get_form_kwargs())


class PreviewCreateView(CreateView):
	def form_valid(self, form):
		item = form.save(commit = False)
		if not 'create' in self.request.POST:
			return self.render_to_response(self.get_context_data(form = form, item = item, valid = True))
		return super(PreviewCreateView, self).form_valid(form)


class PreviewUpdateView(UpdateView):
	def form_valid(self, form):
		item = form.save(commit = False)
		if not 'update' in self.request.POST:
			return self.render_to_response(self.get_context_data(form = form, item = item, valid = True))
		return super(PreviewUpdateView, self).form_valid(form)


class DetailUserProtectedView(DetailView):
	published_field = None
	author_field = None
	superuser_perm = None

	def get_queryset(self):
		qs = super(DetailView, self).get_queryset()
		q = []
		if not self.request.user.is_superuser:
			if not self.superuser_perm or not self.user.has_perm(self.superuser_perm):
				if self.published_field:
					q.append(Q(**{self.published_field: True}))
				if self.author_field and self.request.user.is_authenticated():
					q.append(Q(**{self.author_field: self.request.user}))
		if q:
			qs = qs.filter(reduce(lambda a, b: a | b, q))

		return qs

	def get_object(self, queryset = None):
		obj = super(DetailUserProtectedView, self).get_object(queryset)
		if hasattr(obj, 'hit'):
			obj.hit()
		return obj
