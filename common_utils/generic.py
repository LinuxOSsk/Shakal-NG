# -*- coding: utf-8 -*-
from functools import reduce

from django.db.models import Q, Manager
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import CreateView, UpdateView, DetailView, ListView as OriginalListView


# dokumentácia  k viewom tu https://ccbv.co.uk/


class PreviewCreateView(CreateView):
	"""
	Tento view funguje ako náhrada CreateView s djanga, ale vytvorí objekt až keď
	dostane ako POST parameter `create`. Bez neho vyrenderuje len náhľad.
	"""

	context_object_name = 'item'

	def form_valid(self, form):
		item = form.save(commit=False)
		if not 'create' in self.request.POST:
			ctx = self.get_context_data(form=form, valid=True)
			ctx[self.context_object_name] = item
			return self.render_to_response(ctx)
		return super(PreviewCreateView, self).form_valid(form)


class PreviewUpdateView(UpdateView):
	"""
	Tento view funguje ako náhrada UpdateView s djanga, ale aktualizuje objekt až keď
	dostane ako POST parameter `create`. Bez neho vyrenderuje len náhľad.
	"""

	context_object_name = 'item'

	def form_valid(self, form):
		item = form.save(commit=False)
		if not 'update' in self.request.POST:
			ctx = self.get_context_data(form=form, valid=True)
			ctx[self.context_object_name] = item
			return self.render_to_response(ctx)
		return super(PreviewUpdateView, self).form_valid(form)


class DetailUserProtectedView(DetailView):
	"""
	Tento view funguje ako náhrada DetailView z djanga.

	Navyše poskytuje možnosť obmedziť prístup k zobrazeniu objektov. Bežní
	používatelia budú môcť zobraziť len objekty, ktoré sú publikované. Autorovi
	je možné povoliť prístup aj k nepublikovaným poliam. Je možné nastaviť plný
	prístup k všetkým objektom pouívateľom, ktorí majú právo uvedené
	v superuser_perm.

	Parametre:
	published_field -- pole modelu, ktoré označuje, že objekt je pulikovaný
	author_field -- pole modelu, podľa ktorého sa určuje autor
	superuser_perm -- používatelia s tímto právom budú mať prístup k všetkým objektom
	"""

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
		if self.author_field and self.request.user.is_authenticated:
			q.append(Q(**{self.author_field: self.request.user}))
		qs = super(DetailUserProtectedView, self).get_queryset()
		if q:
			return qs.filter(reduce(lambda a, b: a | b, q)) # pylint: disable=no-member
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
	"""
	Náhrada ListView z djanga s podporou kategórií a stránkovania. V urls.py musí
	byť kategória pomenovaná ?P<category>.

	Parametre:
	paginate_by -- počet záznamov na stránku
	category_model -- v tomto modeli sú kategórie, None ak sa kategórie nepoužívajú
	category_key -- kľúč, podľa ktorého sa vyhľadávajú kategórie
	"""

	category_model = None
	category_key = 'slug'
	category_field = 'category'
	category_context = 'category'

	def filter_by_category(self, queryset):
		if isinstance(queryset, Manager):
			queryset = queryset.all()
		if self.category_object is not None:
			queryset = queryset.filter(**{self.category_field: self.category_object})
		return queryset

	def get_queryset(self):
		return self.filter_by_category(super(ListView, self).get_queryset())

	@cached_property
	def category_object(self):
		if 'category' in self.kwargs:
			return get_object_or_404(self.category_model, **{self.category_key: self.kwargs['category']})
		else:
			return None

	def get_context_data(self, **kwargs):
		context = super(ListView, self).get_context_data(**kwargs)
		if self.category_model is not None:
			context['category_list'] = self.category_model.objects.all()
		if self.category_object is not None:
			context[self.category_context] = self.category_object
		return context


class RequestFormViewMixin(object):
	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs
