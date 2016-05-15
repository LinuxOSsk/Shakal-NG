# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import Node
from common_utils.generic import ListView, DetailView


class StoryMixin(object):
	queryset = (Node.objects.all()
		.select_related('revision', 'author')
		.filter(node_type='story')
		.order_by('-pk'))


class StoryList(StoryMixin, ListView):
	paginate_by = 20


class StoryDetail(StoryMixin, DetailView):
	pass
