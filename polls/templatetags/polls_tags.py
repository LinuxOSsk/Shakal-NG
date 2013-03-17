# -*- coding: utf-8 -*-
from django import template
from polls.models import Poll


register = template.Library()


@register.inclusion_tag('polls/block_poll_detail.html', takes_context = True)
def polls_frontpage(context):
	return {'polls': Poll.objects.all()[:1], 'request': context['request']}
