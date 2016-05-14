# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import Node
from common_utils.generic import ListView


class StoryList(ListView):
	queryset = Node.objects.all().select_related('revision', 'author').filter(node_type='story')
	paginate_by = 20
