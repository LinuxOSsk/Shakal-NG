# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from haystack.views import SearchView as HaystackSearchView
from haystack.forms import HighlightedModelSearchForm


class SearchView(HaystackSearchView):
	def __init__(self, *args, **kwargs):
		if not 'form_class' in kwargs:
			kwargs['form_class'] = HighlightedModelSearchForm
		super(SearchView, self).__init__(*args, **kwargs)

	def create_response(self):
		context = {
			'query': self.query,
			'form': self.form,
			'suggestion': None,
			'results': self.results,
			'pagenum': self.request.GET.get('page', 1),
		}

		if self.results and hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
			context['suggestion'] = self.form.get_suggestion()

		context.update(self.extra_context())
		return render_to_response(self.template, context, context_instance=self.context_class(self.request))
