# -*- coding: utf-8 -*-
import cStringIO
import datetime

import csv
import qsstats
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.utils.translation import ugettext as _
from simplejson import dumps

from article.models import Article
from news.models import News
from threaded_comments.models import Comment


@staff_member_required
def stats(request):
	def generate_choices(content_type):
		return [
			{'label': _('30 days'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-30&end_day=0'},
			{'label': _('60 days'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-60&end_day=0'},
			{'label': _('1 year (sum 30 days)'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-365&end_day=0&interval=days&aggregate=30'},
			{'label': _('1 year (weekly)'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-365&end_day=0&interval=weeks'},
			{'label': _('2 years (sum 30 days)'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-730&end_day=0&interval=days&aggregate=30'},
			{'label': _('2 years (weekly)'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-730&end_day=0&interval=weeks'},
			{'label': _('2 years (sum 4 weeks)'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-730&end_day=0&interval=weeks&aggregate=4'},
			{'label': _('2 years (monthly)'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-730&end_day=0&interval=months'},
			{'label': _('4 years (weekly)'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-1460&end_day=0&interval=weeks'},
			{'label': _('4 years (sum 4 weeks)'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-1460&end_day=0&interval=weeks&aggregate=4'},
			{'label': _('4 years (monthly)'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-1460&end_day=0&interval=months'},
			{'label': _('8 years (weekly)'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-2920&end_day=0&interval=weeks'},
			{'label': _('8 years (sum 4 weeks)'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-2920&end_day=0&interval=weeks&aggregate=4'},
			{'label': _('8 years (monthly)'), 'url': data_link + '?type=' + content_type + '&interval=days&start_day=-2920&end_day=0&interval=months'},
		]
	data_link = reverse('admin_dashboard:stats')
	data = [
		(
			'comments', {
				'name': _('Comments'),
				'qs': Comment.objects.exclude(parent_id = 0),
				'date_col': 'submit_date',
				'choices': generate_choices('comments'),
			}
		),
		(
			'news', {
				'name': _('News'),
				'date_col': 'created',
				'qs': News.objects.filter(approved = True),
				'choices': generate_choices('news'),
			}
		),
		(
			'articles', {
				'name': _('Articles'),
				'date_col': 'pub_time',
				'qs': Article.objects.all(),
				'choices': generate_choices('articles')[4:],
			}
		),
	]
	if 'type' in request.GET:
		data_info = dict(data)[request.GET['type']]
		data = [(_('Date'), data_info['name'])]

		interval = request.GET.get('interval', 'days')
		start_day = int(request.GET.get('start_day', -30))
		end_day = int(request.GET.get('end_day', 0))
		if start_day > end_day:
			raise ValueError("End day before start day")
		aggregate = int(request.GET.get('aggregate', 1))

		if aggregate > 60 or aggregate <= 0:
			raise ValueError("Bad value for aggregate")

		intervals = {
			'days': 1,
			'weeks': 7,
			'months': 31,
			'years': 365,
		}

		interval_days = end_day - start_day
		if interval in intervals:
			interval_values = interval_days / intervals[interval]
			start_day = start_day - aggregate * intervals[interval]
		else:
			raise ValueError("Bad value for interval")
		if interval_values > 1000:
			raise ValueError("Too many values")

		today = datetime.date.today()
		start_date = today + datetime.timedelta(days = start_day)
		end_date = today + datetime.timedelta(days = end_day)

		qss = qsstats.QuerySetStats(data_info['qs'], data_info['date_col'])
		time_series = qss.time_series(start_date, end_date, interval = interval)

		time_series_sum = time_series[:]
		for i in range(len(time_series_sum)):
			if i - 1 >= 0:
				acc = time_series_sum[i - 1][1]
			else:
				acc = 0
			acc += time_series[i][1]
			if i - aggregate >= 0:
				acc -= time_series[i - aggregate][1]
			time_series_sum[i] = (time_series_sum[i][0], acc)

		data += [(t[0].strftime("%Y-%m-%d"), t[1]) for t in time_series_sum[aggregate - 1:]]
	else:
		for obj in data:
			del obj[1]['qs']
	fmt = request.GET.get('format', 'json')
	if fmt == 'json':
		return HttpResponse(dumps(data))
	elif fmt == 'csv':
		f = cStringIO.StringIO()
		writer = csv.writer(f, delimiter = ',')
		for row in data:
			writer.writerow([unicode(s).encode("utf-8") for s in row])
		return HttpResponse(f.getvalue())
