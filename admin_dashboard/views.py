# -*- coding: utf-8 -*-
import datetime
from io import StringIO
from json import dumps

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.http.response import HttpResponse
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.translation import gettext as _
from django.views.generic import View

from article.models import Article
from comments.models import Comment
from common_utils.time_series import time_series as get_time_series, set_gaps_zero
from news.models import News


class Stats(UserPassesTestMixin, View):
	def generate_choices(self, content_type):
		data_link = reverse('admin_dashboard:stats')
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

	@property
	def data(self):
		return [
			(
				'comments', {
					'name': _('Comments'),
					'qs': Comment.objects.all().exclude(parent_id = 0),
					'date_col': 'created',
					'choices': self.generate_choices('comments'),
				}
			),
			(
				'news', {
					'name': _('News'),
					'date_col': 'created',
					'qs': News.objects.all().filter(approved = True),
					'choices': self.generate_choices('news'),
				}
			),
			(
				'articles', {
					'name': _('Articles'),
					'date_col': 'pub_time',
					'qs': Article.objects.all(),
					'choices': self.generate_choices('articles')[4:],
				}
			),
		]

	def format_data(self, data, fmt):
		if fmt == 'csv':
			f = StringIO()
			for row in data:
				f.write(','.join([force_str(s) for s in row]) + '\n')
			return HttpResponse(f.getvalue())
		else: # json
			return HttpResponse(dumps(data))

	def get_interval(self, request):
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
		start_date = today + datetime.timedelta(days=start_day)
		end_date = today + datetime.timedelta(days=end_day)

		return start_date, end_date, interval, aggregate

	def acumulate(self, time_series, aggregate):
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

		return [(t[0].strftime("%Y-%m-%d"), t[1]) for t in time_series_sum[aggregate - 1:]]

	def get(self, request, *args, **kwargs):
		if 'type' in request.GET:
			data_info = dict(self.data)[request.GET['type']]
			data = [(_('Date'), data_info['name'])]

			start_date, end_date, interval, aggregate = self.get_interval(request)

			time_series = set_gaps_zero(get_time_series(
				data_info['qs'],
				date_field=data_info['date_col'],
				aggregate=Count('id'),
				interval=interval[:-1],
				date_from=start_date,
				date_to=end_date
			))
			data += self.acumulate(time_series, aggregate)
		else:
			data = self.data
			for obj in data:
				del obj[1]['qs']
		return self.format_data(data, request.GET.get('format', 'json'))

	def test_func(self):
		user = self.request.user
		return user.is_authenticated and user.is_staff
