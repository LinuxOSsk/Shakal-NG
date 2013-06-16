# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.views.generic import CreateView, UpdateView, DetailView, ListView as OriginalListView


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


class ListView(OriginalListView):
	category = None
	category_key = 'slug'

	def get_queryset(self):
		queryset = super(ListView, self).get_queryset()
		if self.category is not None:
			category_object = None
			if 'category' in self.kwargs:
				category_object = get_object_or_404(self.category, **{self.category_key: self.kwargs['category']})
				queryset = queryset.filter(category = category_object)
			self.kwargs['category_object'] = category_object
		return queryset

	def get_context_data(self, **kwargs):
		queryset = kwargs.pop('object_list')
		context_object_name = self.get_context_object_name(queryset)
		context = {'object_list': queryset}
		if context_object_name is not None:
			context[context_object_name] = queryset
		if 'category_object' in self.kwargs:
			context['category'] = self.kwargs['category_object']
		context.update(kwargs)
		page = self.kwargs.get(self.page_kwarg) or self.request.GET.get(self.page_kwarg) or 1
		context['page'] = page
		return context
