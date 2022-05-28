# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import datetime, date, time, timedelta
from functools import partial

from django.db import models
from django.db.models import DateField, DateTimeField
from django.db.models.functions import Trunc
from django.utils import timezone


DATETIME_SERIES = set(['minute', 'hour'])
DATE_SERIES = set(['day', 'week', 'month', 'year'])


TICKS = {
	'minute': lambda ts: ts + timedelta(seconds=60),
	'hour': lambda ts: ts + timedelta(seconds=3600),
	'day': lambda ts: ts + timedelta(1),
	'week': lambda ts: ts + timedelta(7),
	'month': lambda ts: date(ts.year if ts.month < 12 else ts.year + 1, ts.month % 12 + 1, 1),
	'year': lambda ts: date(ts.year + 1, 1, 1),
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


def time_series(qs, date_field, aggregate, interval, date_from=None, date_to=None): # pylint: disable=too-many-arguments
	current_timezone = timezone.get_current_timezone()
	is_date = interval in DATE_SERIES

	if isinstance(qs.model._meta.get_field(date_field), models.DateTimeField):
		db_interval = Trunc(date_field, interval, output_field=DateTimeField(), tzinfo=current_timezone)
	else:
		db_interval = Trunc(date_field, interval, output_field=DateField())

	if not isinstance(aggregate, dict):
		aggregate = {'aggregate': aggregate}

	SeriesRecord = namedtuple('SeriesRecord', ['time_value'] + list(aggregate.keys()))

	if is_date:
		if date_from and not isinstance(date_from, datetime):
			date_from = datetime.combine(date_from, time.min, current_timezone)
		if date_to and not isinstance(date_to, datetime):
			date_to = datetime.combine(date_to, time.max, current_timezone)

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


def set_gaps_zero(data):
	return [record.__class__(*(0 if val is None else val for val in record)) for record in data]


def sum_weeks(data):
	if len(data) == 0:
		return data
	current = None
	last_time = None
	weekly = []
	record_cls = data[0].__class__

	for record in data:
		if last_time != record.time_value - timedelta(record.time_value.weekday()):
			if current is not None:
				weekly.append(record_cls(last_time, *current)) # pylint: disable=not-an-iterable
			current = [0] * (len(data[0]) - 1)
			last_time = record.time_value - timedelta(record.time_value.weekday())
		for i in range(len(data[0]) - 1):
			current[i] += record[i + 1]

	weekly.append(record_cls(last_time, *current))
	return weekly
