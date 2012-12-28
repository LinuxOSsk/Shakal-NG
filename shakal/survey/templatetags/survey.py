# -*- coding: utf-8 -*-

from django import template
from shakal.survey.models import Survey

register = template.Library()

@register.inclusion_tag('survey/block_survey_detail.html', takes_context = True)
def survey_frontpage(context):
	survey = Survey.surveys.all()
	context.update({'survey': ''})
	if not survey:
		return context
	context.update({'survey': survey[0]})
	return context
