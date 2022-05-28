# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ngettext
from django.views.generic import ListView, FormView

from .forms import FlagForm
from .models import Rating, Statistics
from .settings import FLAG_CONTENT_TYPES
from comments.views import get_module_name, get_module_url
from common_utils import get_meta
from notifications.models import Event


class FlagView(LoginRequiredMixin, FormView):
	form_class = FlagForm
	template_name = 'rating/flag_form.html'

	@cached_property
	def object_content_type(self):
		ctypes_query = Q()
		for app_name, model_name in FLAG_CONTENT_TYPES:
			ctypes_query |= Q(app_label=app_name, model=model_name)
		content_types = ContentType.objects.filter(ctypes_query)
		return get_object_or_404(content_types, pk=self.kwargs['content_type'])

	@cached_property
	def flagged_object(self):
		return get_object_or_404(self.object_content_type.model_class(), pk=self.kwargs['object_id'])

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
		instance = form.save()
		model = self.flagged_object.__class__
		model_name = model._meta.verbose_name
		model_name = model_name[:1].lower() + model_name[1:]
		statistics = Statistics.objects.get_statistics(self.flagged_object)
		if statistics.flag_count:
			flagged_message = ngettext(
				'%(num)s user flagged this %(content_type)s',
				'%(num)s users flagged this %(content_type)s',
				statistics.flag_count
			) % {'num': statistics.flag_count, 'content_type': model_name}
			event, created = Event.objects.get_or_create(
				content_type=ContentType.objects.get_for_model(model),
				object_id=self.flagged_object.pk,
				action=Event.FLAG_ACTION,
				defaults={
					'level': messages.WARNING,
					'author': self.request.user,
					'message': flagged_message,
					'linked_type': ContentType.objects.get_for_model(instance.__class__),
					'linked_id': instance.pk,
				}
			)
			if not created:
				Event.objects.filter(pk=event.pk).update(
					message=flagged_message,
					linked_type=ContentType.objects.get_for_model(instance.__class__),
					linked_id=instance.pk
				)
			Event.objects.broadcast_event(
				event,
				permissions=(model, 'change_' + model._meta.model_name)
			)
		return HttpResponseRedirect(self.get_success_url())

	def get_success_url(self):
		return self.flagged_object.get_absolute_url()


class RatingsView(UserPassesTestMixin, ListView):
	@cached_property
	def object(self):
		return get_object_or_404(Rating, pk=self.kwargs['pk'])

	def test_func(self):
		return self.request.user.is_staff

	def get_queryset(self):
		return (Rating.objects
			.exclude(marked_flag=Rating.FLAG_NONE)
			.filter(statistics_id=self.object.statistics_id)
			.select_related('user')
			.order_by('-pk'))

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		content_object = self.object.statistics.content_object
		ctx.update({
			'object_type_verbose_name': get_meta(content_object).verbose_name if content_object else '',
			'object': self.object,
		})
		return ctx

	def post(self, request, *args, **kwargs):
		if request.POST.get('manage'):
			stat = self.object.statistics
			content_object = stat.content_object
			Event.objects.deactivate(content_object=(stat.object_id, stat.content_type), action_type=Event.FLAG_ACTION)
			if content_object:
				return HttpResponseRedirect(content_object.get_absolute_url())
			else:
				return HttpResponseRedirect(reverse('home'))
		return HttpResponseBadRequest()
