# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def feeds(request):
	return {'feeds': getattr(request, '_feeds', [])}
