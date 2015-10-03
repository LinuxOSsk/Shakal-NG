# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple
from datetime import datetime, date, time, timedelta
from functools import partial

from django.db import models
from django.db.models.expressions import DateTime, Date
from django.utils import timezone

from common_utils import get_meta


DATETIME_SERIES = set(['minute', 'hour'])
DATE_SERIES = set(['day', 'month', 'year'])


def add_minute(ts):
	return ts + timedelta(seconds=60)


def add_hour(ts):
	return ts + timedelta(seconds=3600)


def add_day(ts):
	return ts + timedelta(1)


def add_month(ts):
	return date(ts.year if ts.month < 12 else ts.year + 1, ts.month % 12 + 1, ts.day)


def add_year(ts):
	return date(ts.year + 1, ts.month, ts.day)


TICKS = {
	'minute': add_minute,
	'hour': add_hour,
	'day': add_day,
	'month': add_month,
	'year': add_year,
}


def fill_time_series_gap(records, empty_record, interval, date_from, date_to):
	if not date_from or not date_to:
		return records

	tick_fn = TICKS[interval]
	is_date = interval in DATE_SERIES

	tz = timezone.get_current_timezone()
	if isinstance(date_from, datetime):
		date_from = date_from.astimezone(tz)
	if isinstance(date_to, datetime):
		date_to = date_to.astimezone(tz)

	if is_date:
		if isinstance(date_from, datetime):
			date_from = date_from.date()
		if isinstance(date_to, datetime):
			date_to = date_to.date()

	filled = []

	last_time = date_from

	for record in records:
		item_time = record.time_value
		while last_time < item_time:
			filled.append(empty_record(last_time))
			last_time = tick_fn(last_time)

		filled.append(record)
		last_time = tick_fn(last_time)

	while last_time <= date_to:
		filled.append(empty_record(last_time))
		last_time = tick_fn(last_time)

	return filled


def time_series(qs, date_field, aggregate, interval, date_from=None, date_to=None):
	current_timezone = timezone.get_current_timezone()
	is_date = interval in DATE_SERIES

	if isinstance(get_meta(qs.model).get_field(date_field), models.DateTimeField):
		db_interval = DateTime(date_field, interval, current_timezone)
	else:
		db_interval = Date(date_field, interval)

	if not isinstance(aggregate, dict):
		aggregate = {'aggregate': aggregate}

	SeriesRecord = namedtuple('SeriesRecord', ['time_value'] + aggregate.keys())

	if is_date:
		if date_from and not isinstance(date_from, datetime):
			date_from = current_timezone.localize(datetime.combine(date_from, time.min))
		if date_to and not isinstance(date_to, datetime):
			date_to = current_timezone.localize(datetime.combine(date_to, time.max))

	if date_from is not None:
		qs = qs.filter(**{date_field + '__gte': date_from})
	if date_to is not None:
		qs = qs.filter(**{date_field + '__lte': date_to})

	qs = (qs
		.annotate(time_value=db_interval)
		.values_list('time_value')
		.order_by('time_value')
		.annotate(**aggregate)
		)

	def convert_date(val):
		if is_date and isinstance(val, datetime):
			return val.date()
		return val

	records = [SeriesRecord(convert_date(val[0]), *val[1:]) for val in qs]

	if len(records):
		date_from = date_from or records[0].time_value
		date_to = date_to or records[-1].time_value

	empty_record = partial(SeriesRecord, **{k: None for k in aggregate.keys()})

	return fill_time_series_gap(records, empty_record, interval, date_from, date_to)


# example:
#
# time_series(
#     User.objects.all(),
#     date_field='date_joined',
#     aggregate={'count': Count('id')},
#     interval='day',
#     date_to=timezone.localtime(timezone.now()).date()
# )
#
# [SeriesRecord(time_value=datetime.date(2015, 9, 17), count=10),
#  SeriesRecord(time_value=datetime.date(2015, 9, 18), count=None),
#  SeriesRecord(time_value=datetime.date(2015, 9, 19), count=None),
#  ...
