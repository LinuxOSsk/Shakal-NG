# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.db.models import Q, Manager
from django.views.generic import CreateView, UpdateView, DetailView, ListView as OriginalListView


class AddLoggedFormArgumentMixin(object):
	author_field = 'author'
	authors_name_field = 'authors_name'

	def get_form(self, form_class):
		return form_class(logged = self.request.user.is_authenticated(), request = self.request, **self.get_form_kwargs())

	def form_valid(self, form):
		obj = form.save(commit = False)
		if hasattr(obj, self.authors_name_field):
			if self.request.user.is_authenticated():
				if self.request.user.get_full_name():
					setattr(obj, self.authors_name_field, self.request.user.get_full_name())
				else:
					setattr(obj, self.authors_name_field, self.request.user.username)
		if hasattr(obj, self.author_field) and self.request.user.is_authenticated():
			setattr(obj, self.author_field, self.request.user)
		return super(AddLoggedFormArgumentMixin, self).form_valid(form)


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


class UpdateProtectedView(UpdateView):
	author_field = None
	unprivileged_queryset = None

	def get_queryset(self):
		if self.unprivileged_queryset:
			return self.unprivileged_queryset
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
		if self.unprivileged_queryset:
			return self.unprivileged_queryset
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

	def get_object(self, queryset = None):
		obj = super(DetailUserProtectedView, self).get_object(queryset)
		if hasattr(obj, 'hit'):
			obj.hit()
		return obj


class ListView(OriginalListView):
	category = None
	category_key = 'slug'
	category_field = 'category'
	category_context = 'category'

	def get_queryset(self):
		queryset = super(ListView, self).get_queryset()
		if isinstance(queryset, Manager):
			queryset = queryset.all()
		if self.category is not None:
			category_object = None
			view_kwargs = getattr(self, 'kwargs')
			if 'category' in view_kwargs:
				category_object = get_object_or_404(self.category, **{self.category_key: view_kwargs['category']})
				queryset = queryset.filter(**{self.category_field: category_object})
			view_kwargs['category_object'] = category_object
		return queryset

	def get_context_data(self, **kwargs):
		queryset = kwargs.pop('object_list')
		if isinstance(queryset, Manager):
			queryset = queryset.all()
		context_object_name = self.get_context_object_name(queryset)
		context = {'object_list': queryset}
		if context_object_name is not None:
			context[context_object_name] = queryset
		if self.category:
			context['category_list'] = self.category.objects.all()
		view_kwargs = getattr(self, 'kwargs')
		if 'category_object' in view_kwargs:
			context[self.category_context] = view_kwargs['category_object']
		context.update(kwargs)
		page = view_kwargs.get(self.page_kwarg) or self.request.GET.get(self.page_kwarg) or 1
		context['page'] = page
		return context
