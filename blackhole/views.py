# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import Node
from common_utils.generic import ListView


class StoryList(ListView):
	paginate_by = 20
	queryset = (Node.objects.all()
		.select_related('revision', 'author')
		.filter(node_type='story')
		.order_by('-pk'))
