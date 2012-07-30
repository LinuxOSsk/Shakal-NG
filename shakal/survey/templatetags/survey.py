# -*- coding: utf-8 -*-

from django import template
from datetime import datetime
from shakal.survey.models import Survey

register = template.Library()

@register.inclusion_tag('survey/block_survey_detail.html', takes_context = True)
def survey_frontpage(context):
	context.update({'survey': Survey.objects.filter(approved = True, content_type = None, active_from__lte = datetime.now()).order_by('-active_from')[0]})
	return context
