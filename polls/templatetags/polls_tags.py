# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_jinja import library
from jinja2 import pass_context

from polls.models import Poll


@library.global_function
@pass_context
def polls_frontpage(context):
	ctx = context.get_all()
	ctx.update({
		'polls': Poll.objects.all()[:1],
		'request': context['request'],
		'user': context['user'],
	})
	return mark_safe(render_to_string('polls/partials/poll_detail.html', ctx))
