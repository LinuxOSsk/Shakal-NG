# -*- coding: utf-8 -*-
from django import template
from django.template.loader import render_to_string
from django_jinja import library
from jinja2 import contextfunction
from jinja2 import nodes

from polls.models import Poll


register = template.Library()
lib = library.Library()


@lib.global_function
@contextfunction
@register.simple_tag(takes_context=True)
def polls_frontpage(context):
	ctx = context.get_all()
	ctx.update({
		'polls': Poll.objects.all()[:1],
		'request': context['request'],
		'user': context['user'],
	})
	return render_to_string('polls/block_poll_detail.html', ctx)
