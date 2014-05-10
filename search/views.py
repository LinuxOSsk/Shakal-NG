# -*- coding: utf-8 -*-
from django.core.paginator import InvalidPage
from django.http import Http404
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from haystack.views import SearchView as HaystackSearchView

from .forms import SearchForm
from paginator.paginator import Paginator


class SearchView(HaystackSearchView):
	paginate_by = 20
	paginator_class = Paginator
	page_kwarg = 'page'

	def __init__(self, *args, **kwargs):
		if not 'form_class' in kwargs:
			kwargs['form_class'] = SearchForm
		super(SearchView, self).__init__(*args, **kwargs)

	def paginate_queryset(self, queryset, page_size):
		paginator = self.paginator_class(queryset, page_size)
		page_kwarg = self.page_kwarg
		page = self.request.GET.get(page_kwarg) or 1
		try:
			page_number = int(page)
		except ValueError:
			raise Http404(_("Page is not number."))

		try:
			page = paginator.page(page_number)
			return (paginator, page, page.object_list, page.has_other_pages())
		except InvalidPage as e:
			raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {'page_number': page_number, 'message': str(e)})


	def create_response(self):
		queryset = self.results
		paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, self.paginate_by)

		context = {
			'query': self.query,
			'form': self.form,
			'suggestion': None,
			'paginator': paginator,
			'page_obj': page,
			'results': queryset,
			'is_paginated': is_paginated,
		}

		if self.results and hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
			context['suggestion'] = self.form.get_suggestion()

		context.update(self.extra_context())
		return render_to_response(self.template, context, context_instance=self.context_class(self.request))
