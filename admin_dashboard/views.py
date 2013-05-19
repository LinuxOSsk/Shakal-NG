# -*- coding: utf-8 -*-
from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import HttpResponse
from threaded_comments.models import Comment
import qsstats
import datetime
from simplejson import dumps


@staff_member_required
def stats(request):
	today = datetime.date.today()
	first_date = today - datetime.timedelta(days = 365 * 2 + 30)
	qs = Comment.objects.exclude(parent_id = 0)
	qss = qsstats.QuerySetStats(qs, 'submit_date')
	time_series = qss.time_series(first_date, today)
	time_series_sum = time_series[:]
	for i, item in enumerate(time_series_sum):
		if i - 1 >= 0:
			acc = time_series_sum[i - 1][1]
		else:
			acc = 0
		acc += time_series[i][1]
		if i - 31 >= 0:
			acc -= time_series[i - 31][1]
		time_series_sum[i] = (time_series_sum[i][0], acc)

	return HttpResponse(dumps([(u'Dutám', u'Komentáre mesačne')] + [(t[0].strftime("%Y-%m"), t[1]) for t in time_series_sum[30:]]))
