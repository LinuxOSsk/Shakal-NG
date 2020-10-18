# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import cached_property
from django.views.generic import ListView

from .forms import SearchForm
from .models import SearchIndex
from fulltext.api import search


class SearchView(ListView):
	template_name = 'search/search.html'
	paginate_by = 20
	context_object_name = 'results'

	def get_queryset(self):
		if self.form.is_valid():
			data = self.form.cleaned_data
			search_document = True
			search_comments = True
			if data['content']:
				search_document = 'document' in data['content']
				search_comments = 'comments' in data['content']
			results = (search(data['q'], search_document=search_document, search_comments=search_comments)
				.select_related('content_type')
				.prefetch_related('content_object')
				.order_by(data['ordering'] or '-rank'))
			if data['models']:
				ctypes = [ContentType.objects.get_by_natural_key(*model.split('.')) for model in data['models']]
				results = results.filter(content_type__in=ctypes)
			return results
		else:
			return SearchIndex.objects.none()

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['form'] = self.form
		if self.form.is_valid():
			ctx['query'] = self.form.cleaned_data['q']
		return ctx

	@cached_property
	def form(self):
		return SearchForm(self.request.GET or None)
