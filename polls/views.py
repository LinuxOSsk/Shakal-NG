# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import FormView

from .forms import PollForm, VoteForm
from .models import Poll, Choice
from common_utils.generic import ListView, DetailView, CreateView


class PollPost(FormView):
	form_class = VoteForm
	object = None

	def post(self, request, **kwargs):
		self.object = get_object_or_404(Poll.active_polls.all(), pk=self.kwargs['pk'])
		return super(PollPost, self).post(request, **kwargs)

	def get_message_tag(self):
		return self.request.POST.get('msg_id', 'polls') # identifikácia ankety ak ich je na webe viacej

	def get_next_url(self):
		return self.request.POST.get('next', '/')

	def get_success_url(self):
		return self.get_next_url()

	def get_form_kwargs(self):
		kwargs = super(PollPost, self).get_form_kwargs()
		kwargs['poll'] = self.object
		return kwargs

	def form_invalid(self, form):
		messages.error(self.request, 'Vyberte prosím odpoveď.', extra_tags=self.get_message_tag())
		return HttpResponseRedirect(self.get_next_url())

	def form_valid(self, form):
		choices = form.cleaned_data['choice']
		if not self.object.checkbox:
			choices = [choices[0]]

		with transaction.atomic():
			if not self.object.can_vote(self.request):
				messages.error(self.request, 'Hlasovať je možné len raz.', extra_tags=self.get_message_tag())
				return HttpResponseRedirect(self.request.POST['next'])

			Poll.objects.filter(pk=self.object.pk).update(choice_count=F('choice_count') + 1)
			self.object.choice_set.filter(pk__in=[c.id for c in choices]).update(votes=F('votes') + 1)
			self.object.record_vote(self.request)
			messages.success(self.request, 'Hlas bol prijatý.', extra_tags=self.get_message_tag())

		return super(PollPost, self).form_valid(form)


class PollCreate(LoginRequiredMixin, CreateView):
	model = Poll
	form_class = PollForm

	def form_valid(self, form):
		super(PollCreate, self).form_valid(form)
		poll = self.object
		choices = [Choice(poll=poll, choice=choice['choice']) for choice in form.cleaned_data['choices']]
		Choice.objects.bulk_create(choices)
		messages.success(self.request, 'Anketa bola vytvorená')
		return HttpResponseRedirect(reverse('home'))


class PollDetail(DetailView):
	queryset = Poll.objects.filter(content_type__isnull=True)
	context_object_name = 'poll'


class PollList(ListView):
	queryset = Poll.objects.filter(content_type__isnull=True)
	paginate_by = 10
	context_object_name = 'polls'
