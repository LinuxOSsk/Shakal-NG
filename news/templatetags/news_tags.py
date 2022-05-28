# -*- coding: utf-8 -*-
from calendar import monthrange
from collections import defaultdict
from datetime import timedelta

from django.template.loader import render_to_string
from django.utils import timezone
from django_jinja import library
from jinja2 import pass_context

from news.models import News


@library.global_function
@pass_context
def news_frontpage(context):
	ctx = {
		'news': News.objects.all().select_related('category')[:10],
		'user': context['user']
	}
	return render_to_string('news/partials/list.html', ctx)


@library.global_function
@pass_context
def news_calendar(context):
	ctx = {
		'user': context['user'],
	}
	today = timezone.localtime(timezone.now()).date()
	start_date = today.replace(day=1)
	end_date = start_date
	end_date += timedelta(monthrange(end_date.year, end_date.month)[1])
	end_date += timedelta(monthrange(end_date.year, end_date.month)[1]-1)
	news = (News.objects
		.filter(event_date__isnull=False, event_date__gte=start_date, event_date__lte=end_date)
		.only('pk', 'title', 'slug', 'event_date', 'author')
		.order_by('-pk'))
	news_by_date = defaultdict(lambda: defaultdict(list))
	for event in news:
		news_by_date[event.event_date.replace(day=1)][event.event_date].append(event)
	if not news_by_date:
		return ''
	news_months = sorted(news_by_date.keys())
	calendars = []
	for month in news_months:
		weeks = []
		calendar = {
			'month': month,
			'weeks': weeks,
		}
		calendars.append(calendar)
		week = []
		month_days = monthrange(month.year, month.month)[1]
		weekday = 0
		for day in range(1, month_days + 1):
			day = month.replace(day=day)
			weekday = day.weekday()
			if day.day == 1:
				for extra_day in range(-weekday, 0):
					week.append({
						'day': day + timedelta(extra_day),
						'extra': True,
						'events': [],
					})
			week.append({
				'day': day,
				'events': news_by_date[month][day],
			})
			if weekday == 6:
				weeks.append(week)
				week = []
		if week:
			for extra_day in range(1, 7-weekday):
				week.append({
					'day': day + timedelta(extra_day),
					'extra': True,
					'events': [],
				})
			weeks.append(week)
			week = []

	ctx['calendars'] = calendars
	return render_to_string('news/partials/calendar.html', ctx)
