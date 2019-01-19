# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import FormView

from .forms import FlagForm
from .models import Rating
from comments.views import get_module_name, get_module_url
from common_utils import get_meta


FLAG_CONTENT_TYPES = (
	('comments', 'comment'),
	('forum', 'topic'),
	('blog', 'blog'),
	('blog', 'post'),
)


class FlagView(LoginRequiredMixin, FormView):
	form_class = FlagForm
	template_name = 'rating/flag_form.html'

	@cached_property
	def content_type(self):
		ctypes_query = Q()
		for app_name, model_name in FLAG_CONTENT_TYPES:
			ctypes_query |= Q(app_label=app_name, model=model_name)
		content_types = ContentType.objects.filter(ctypes_query)
		return get_object_or_404(content_types, pk=self.kwargs['content_type'])

	@cached_property
	def flagged_object(self):
		return get_object_or_404(self.content_type.model_class(), pk=self.kwargs['object_id'])

	@cached_property
	def object(self):
		try:
			return Rating.objects.get_rating(self.flagged_object, self.request.user)
		except Rating.DoesNotExist:
			return None

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['user'] = self.request.user
		kwargs['object'] = self.flagged_object
		kwargs['instance'] = self.object
		return kwargs

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(object=self.flagged_object, **kwargs)
		ctx.update({
			'content_object': self.flagged_object,
			'module_name': get_module_name(self.flagged_object),
			'module_url': get_module_url(self.flagged_object),
			'object_type_verbose_name': get_meta(self.flagged_object).verbose_name.lower(),
			'object': self.object,
		})
		return ctx

	def form_valid(self, form):
		form.save()
		return HttpResponseRedirect(self.get_success_url())

	def get_success_url(self):
		return self.flagged_object.get_absolute_url()
