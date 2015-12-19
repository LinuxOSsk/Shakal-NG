# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q, Manager
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView, ListView as OriginalListView
from django_simple_paginator import Paginator


class PreviewCreateView(CreateView):
	def form_valid(self, form):
		item = form.save(commit=False)
		if not 'create' in self.request.POST:
			return self.render_to_response(self.get_context_data(form=form, item=item, valid=True))
		return super(PreviewCreateView, self).form_valid(form)


class PreviewUpdateView(UpdateView):
	def form_valid(self, form):
		item = form.save(commit=False)
		if not 'update' in self.request.POST:
			return self.render_to_response(self.get_context_data(form=form, item=item, valid=True))
		return super(PreviewUpdateView, self).form_valid(form)


class UpdateProtectedView(UpdateView):
	author_field = None
	unprivileged_queryset = None

	def get_queryset(self):
		if self.unprivileged_queryset is not None:
			return self.unprivileged_queryset.all()
		if self.request.user.is_authenticated():
			return super(UpdateProtectedView, self).get_queryset().filter(**{self.author_field: self.request.user})
		else:
			return super(UpdateProtectedView, self).get_queryset().none()


class DetailUserProtectedView(DetailView):
	published_field = None
	author_field = None
	superuser_perm = None
	unprivileged_queryset = None

	def get_unprivileged_queryset(self):
		if self.unprivileged_queryset is not None:
			return self.unprivileged_queryset.all()
		q = []
		if self.published_field:
			q.append(Q(**{self.published_field: True}))
		if self.author_field and self.request.user.is_authenticated():
			q.append(Q(**{self.author_field: self.request.user}))
		qs = super(DetailUserProtectedView, self).get_queryset()
		if q:
			return qs.filter(reduce(lambda a, b: a | b, q))
		else:
			return qs

	def get_queryset(self):
		qs = super(DetailUserProtectedView, self).get_queryset()
		if self.superuser_perm and self.request.user.has_perm(self.superuser_perm):
			return qs
		if self.request.user.is_superuser:
			return qs
		return self.get_unprivileged_queryset()

	def get_object(self, queryset=None):
		obj = super(DetailUserProtectedView, self).get_object(queryset)
		if hasattr(obj, 'hit'):
			obj.hit()
		return obj


class ListView(OriginalListView):
	category_model = None
	category_key = 'slug'
	category_field = 'category'
	category_context = 'category'
	category_object = None
	paginator_class = Paginator

	def get_queryset(self):
		queryset = super(ListView, self).get_queryset()
		if isinstance(queryset, Manager):
			queryset = queryset.all()
		if self.category_model is not None:
			category_object = None
			if 'category' in self.kwargs:
				category_object = get_object_or_404(self.category_model, **{self.category_key: self.kwargs['category']})
				queryset = queryset.filter(**{self.category_field: category_object})
			self.category_object = category_object
		return queryset

	def get_context_data(self, **kwargs):
		context = super(ListView, self).get_context_data(**kwargs)
		if self.category_model:
			context['category_list'] = self.category_model.objects.all()
		if self.category_object:
			context[self.category_context] = self.category_object
		return context
