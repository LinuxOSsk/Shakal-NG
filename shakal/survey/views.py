# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.template import RequestContext
from django.views.decorators.http import require_POST
from datetime import datetime
from forms import SurveyForm
from models import Survey, Answer, check_can_vote, record_vote
from shakal.utils import unique_slugify


@require_POST
def post(request, pk):
	survey = get_object_or_404(Survey, pk = pk)

	tag = request.POST.get('msg_id', 'survey')

	if not survey.approved:
		messages.error(request, 'Anketa nie je schválená.', extra_tags = tag)
		return HttpResponseRedirect(request.POST['next'])

	if not 'answer' in request.POST:
		messages.error(request, 'Vyberte prosím odpoveď.', extra_tags = tag)
		return HttpResponseRedirect(request.POST['next'])

	if not survey.checkbox:
		answers = [int(request.POST['answer'])]

	if survey.checkbox:
		answers = [int(answer) for answer in request.POST.getlist('answer')]
		if len(answers) == 0:
			messages.error(request, 'Vyberte prosím odpoveď.', extra_tags = tag)
			return HttpResponseRedirect(request.POST['next'])

	if not check_can_vote(request, survey):
		messages.error(request, 'Hlasovať je možné len raz.', extra_tags = tag)
		return HttpResponseRedirect(request.POST['next'])

	answer_objects = survey.answer_set.order_by('pk').values_list('pk', flat = True)
	update_answer_objects = []
	for answer in answers:
		update_answer_objects.append(answer_objects[answer])

	Survey.objects.filter(pk = survey.pk).update(answer_count = F('answer_count') + 1)
	survey.answer_set.filter(pk__in = update_answer_objects).update(votes = F('votes') + 1)

	record_vote(request, survey)

	messages.success(request, 'Hlas bol prijatý.', extra_tags = 'survey')
	return HttpResponseRedirect(request.POST['next'])


@login_required
def create(request):
	if request.method == 'POST':
		form = SurveyForm(request.POST)
		if form.is_valid():
			survey = form.save(commit = False)
			unique_slugify(survey, title_field = 'question')
			survey.save()
			answers = [Answer(survey = survey, answer = a['answer']) for a in form.cleaned_data['answers']]
			Answer.objects.bulk_create(answers)
			return HttpResponseRedirect(survey.get_absolute_url())
	else:
		form = SurveyForm()

	context = {
		'form': form
	}
	return TemplateResponse(request, "survey/survey_create.html", RequestContext(request, context))


def survey_detail_by_slug(request, slug):
	survey = get_object_or_404(Survey, slug = slug, content_type = None)
	context = {
		'survey': survey
	}
	return TemplateResponse(request, "survey/survey_detail.html", RequestContext(request, context))


def survey_list(request, page = 1):
	context = {
		'surveys': Survey.objects.filter(approved = True, content_type = None, active_from__lte = datetime.now()).order_by('-pk').all(),
		'pagenum': page,
	}
	return TemplateResponse(request, "survey/survey_list.html", RequestContext(request, context))
