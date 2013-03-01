# -*- coding: utf-8 -*-

from django import template
from shakal.survey.models import Survey

register = template.Library()

@register.inclusion_tag('survey/block_survey_detail.html', takes_context = True)
def survey_frontpage(context):
	return {'surveys': Survey.surveys.all()[:1]}
