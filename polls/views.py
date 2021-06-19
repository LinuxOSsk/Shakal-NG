# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import FormView

from .forms import PollForm, VoteForm
from .models import Poll, Choice
from common_utils.generic import ListView, DetailView, CreateView


class PollPost(FormView):
	form_class = VoteForm
	object = None

	def dispatch(self, request, *args, **kwargs):
		self.object = get_object_or_404(Poll.active_polls.all(), pk=self.kwargs['pk'])
		return super(PollPost, self).dispatch(request, **kwargs)

	def get(self, request, *args, **kwargs):
		return HttpResponseNotAllowed(['POST'])

	def get_message_tag(self):
		return self.request.POST.get('msg_id', 'polls') # identifikácia ankety ak ich je na webe viacej

	def get_success_url(self):
		return self.request.POST.get('next', '/')

	def get_form_kwargs(self):
		kwargs = super(PollPost, self).get_form_kwargs()
		kwargs['poll'] = self.object
		return kwargs

	def form_invalid(self, form):
		messages.error(self.request, "Vyberte prosím odpoveď.", extra_tags=self.get_message_tag())
		return HttpResponseRedirect(self.get_success_url())

	def form_valid(self, form):
		choices = form.cleaned_data['choice']
		if not self.object.checkbox:
			choices = [choices[0]]

		with transaction.atomic():
			if not self.object.can_vote(self.request):
				messages.error(self.request, "Hlasovať je možné len raz.", extra_tags=self.get_message_tag())
				return HttpResponseRedirect(self.get_success_url())

			Poll.objects.filter(pk=self.object.pk).update(answer_count=F('answer_count') + 1)
			self.object.choices.filter(pk__in=[c.id for c in choices]).update(votes=F('votes') + 1)
			self.object.record_vote(self.request)
			messages.success(self.request, "Hlas bol prijatý.", extra_tags=self.get_message_tag())

		return super(PollPost, self).form_valid(form)


class PollCreate(LoginRequiredMixin, CreateView):
	model = Poll
	form_class = PollForm

	def form_valid(self, form):
		super(PollCreate, self).form_valid(form)
		poll = self.object
		choices = [Choice(poll=poll, choice=choice['choice']) for choice in form.cleaned_data['choices']]
		Choice.objects.bulk_create(choices)
		messages.success(self.request, "Anketa bola vytvorená")
		return HttpResponseRedirect(reverse('home'))


class PollDetail(DetailView):
	context_object_name = 'poll'

	def get_queryset(self):
		return Poll.objects.all().filter(content_type__isnull=True)


class PollList(ListView):
	paginate_by = 10
	context_object_name = 'polls'

	def get_queryset(self):
		return Poll.objects.all().filter(content_type__isnull=True)
