# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import View

from .forms import PollForm
from .models import Poll, Choice, check_can_vote, record_vote
from common_utils.generic import ListView, DetailView, CreateView


class PollPost(View):
	def post(self, request, pk):
		poll = get_object_or_404(Poll.active_polls.all(), pk=pk)

		tag = request.POST.get('msg_id', 'polls')

		if not 'choice' in request.POST:
			messages.error(request, 'Vyberte prosím odpoveď.', extra_tags=tag)
			return HttpResponseRedirect(request.POST['next'])

		if not poll.checkbox:
			choices = [int(request.POST['choice'])]

		if poll.checkbox:
			choices = [int(choice) for choice in request.POST.getlist('choice')]
			if len(choices) == 0:
				messages.error(request, 'Vyberte prosím odpoveď.', extra_tags=tag)
				return HttpResponseRedirect(request.POST['next'])

		if not check_can_vote(request, poll):
			messages.error(request, 'Hlasovať je možné len raz.', extra_tags=tag)
			return HttpResponseRedirect(request.POST['next'])

		choice_objects = poll.choice_set.order_by('pk').values_list('pk', flat=True)
		update_choice_objects = []
		for choice in choices:
			update_choice_objects.append(choice_objects[choice])

		Poll.objects.filter(pk=poll.pk).update(choice_count=F('choice_count') + 1)
		poll.choice_set.filter(pk__in=update_choice_objects).update(votes=F('votes') + 1)

		record_vote(request, poll)

		messages.success(request, 'Hlas bol prijatý.', extra_tags=tag)
		return HttpResponseRedirect(request.POST['next'])


class PollCreate(CreateView):
	model = Poll
	form_class = PollForm

	def form_valid(self, form):
		super(PollCreate, self).form_valid(form)
		poll = self.object
		choices = [Choice(poll=poll, choice=a['choice']) for a in form.cleaned_data['choices']]
		Choice.objects.bulk_create(choices)
		messages.success(self.request, 'Anketa bola vytvorená')
		return HttpResponseRedirect(reverse('home'))


class PollDetail(DetailView):
	queryset = Poll.objects.filter(content_type=None)
	context_object_name = 'poll'


class PollList(ListView):
	queryset = Poll.objects.filter(content_type=None)
	paginate_by = 10
	context_object_name = 'polls'
