# -*- coding: utf-8 -*-
def feeds(request):
	return {'feeds': getattr(request, '_feeds', [])}
