# -*- coding: utf-8 -*-

from django.contrib import messages
from django.db.models import F
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from models import Survey

@require_POST
def post(request, pk):
	survey = get_object_or_404(Survey, pk = pk)
	if not 'answer' in request.POST:
		messages.error(request, 'Vyberte prosím odpoveď.', extra_tags = 'survey')
		return HttpResponseRedirect(request.POST['next'])

	if not survey.checkbox:
		answers = [int(request.POST['answer'])]

	if survey.checkbox:
		answers = [int(answer) for answer in request.POST.getlist('answer')]
		if len(answers) == 0:
			messages.error(request, 'Vyberte prosím odpoveď.', extra_tags = 'survey')
			return HttpResponseRedirect(request.POST['next'])

	answer_objects = survey.answer_set.order_by('pk').values_list('pk', flat = True)
	update_answer_objects = []
	for answer in answers:
		update_answer_objects.append(answer_objects[answer])

	Survey.objects.filter(pk = survey.pk).update(answer_count = F('answer_count') + 1)
	survey.answer_set.filter(pk__in = update_answer_objects).update(votes = F('votes') + 1)

	messages.success(request, 'Hlas bol prijatý.', extra_tags = 'survey')
	return HttpResponseRedirect(request.POST['next'])
