# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.template import RequestContext
from django.views.decorators.http import require_POST
from common_utils.generic import ListView
from forms import PollForm
from models import Poll, Choice, check_can_vote, record_vote


@require_POST
def post(request, pk):
	poll = get_object_or_404(Poll, pk = pk)

	tag = request.POST.get('msg_id', 'polls')

	if not poll.approved:
		messages.error(request, 'Anketa nie je schválená.', extra_tags = tag)
		return HttpResponseRedirect(request.POST['next'])

	if not 'choice' in request.POST:
		messages.error(request, 'Vyberte prosím odpoveď.', extra_tags = tag)
		return HttpResponseRedirect(request.POST['next'])

	if not poll.checkbox:
		choices = [int(request.POST['choice'])]

	if poll.checkbox:
		choices = [int(choice) for choice in request.POST.getlist('choice')]
		if len(choices) == 0:
			messages.error(request, 'Vyberte prosím odpoveď.', extra_tags = tag)
			return HttpResponseRedirect(request.POST['next'])

	if not check_can_vote(request, poll):
		messages.error(request, 'Hlasovať je možné len raz.', extra_tags = tag)
		return HttpResponseRedirect(request.POST['next'])

	choice_objects = poll.choice_set.order_by('pk').values_list('pk', flat = True)
	update_choice_objects = []
	for choice in choices:
		update_choice_objects.append(choice_objects[choice])

	Poll.objects.filter(pk = poll.pk).update(choice_count = F('choice_count') + 1)
	poll.choice_set.filter(pk__in = update_choice_objects).update(votes = F('votes') + 1)

	record_vote(request, poll)

	messages.success(request, 'Hlas bol prijatý.', extra_tags = tag)
	return HttpResponseRedirect(request.POST['next'])


@login_required
def create(request):
	if request.method == 'POST':
		form = PollForm(request.POST)
		if form.is_valid():
			poll = form.save(commit = False)
			poll.save()
			choices = [Choice(poll = poll, choice = a['choice']) for a in form.cleaned_data['choices']]
			Choice.objects.bulk_create(choices)
			return HttpResponseRedirect(poll.get_absolute_url())
	else:
		form = PollForm()

	context = {
		'form': form
	}
	return TemplateResponse(request, "polls/poll_create.html", RequestContext(request, context))


def poll_detail_by_slug(request, slug):
	poll = get_object_or_404(Poll, slug = slug, content_type = None)
	context = {
		'poll': poll
	}
	return TemplateResponse(request, "polls/poll_detail.html", RequestContext(request, context))


class PollList(ListView):
	queryset = Poll.objects.all()
	paginate_by = 10
	context_object_name = 'polls'
