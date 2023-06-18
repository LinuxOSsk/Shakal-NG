# -*- coding: utf-8 -*-
from datetime import timedelta, time, datetime
from typing import Tuple

from django.template.loader import select_template
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.safestring import mark_safe

from article.models import Article
from blog.models import Post
from comments.templatetags.comments_tags import add_discussion_attributes
from forum.models import Topic
from linuxos.templatetags.linuxos import get_base_uri
from news.models import News
from tweets.models import Tweet


SENDING_HOUR = 8
TimeRange = Tuple[datetime, datetime]


def get_week_date_range() -> TimeRange:
	today = timezone.now().date()

	week_start = today - timedelta(days=today.weekday() + 7)
	week_end = week_start + timedelta(days=7)

	midnight = time(0)
	tz = timezone.get_current_timezone()

	week_start = timezone.make_aware(datetime.combine(week_start, midnight), tz) + timedelta(hours=SENDING_HOUR)
	week_end = timezone.make_aware(datetime.combine(week_end, midnight), tz) + timedelta(hours=SENDING_HOUR)

	return (week_start, week_end)


def filter_range(queryset, time_range: TimeRange, time_field: str = 'created'):
	time_start, time_end = time_range
	return queryset.filter(**{f'{time_field}__gte': time_start, f'{time_field}__lt': time_end})


def collect_articles(time_range: TimeRange):
	return filter_range(Article.objects
		.order_by('pub_time')
		.defer('original_content', 'filtered_content')
		.select_related('presentation_image'), time_range, 'pub_time')[:50]


def collect_blog_posts(time_range: TimeRange):
	return filter_range(Post.objects
		.order_by('pub_time')
		.defer('original_content', 'filtered_content')
		.select_related('presentation_image'), time_range, 'pub_time')[:50]


def collect_news(time_range: TimeRange):
	return filter_range(News.objects
		.order_by('created'), time_range, 'created')[:200]


def collect_topics(time_range: TimeRange):
	return filter_range(Topic.objects
		.order_by('created'), time_range, 'created')[:200]


def collect_tweets(time_range: TimeRange):
	return filter_range(Tweet.objects
		.order_by('created'), time_range, 'created')[:200]


COLLECTORS = [
	{'name': 'article', 'verbose_name': "Články", 'fn': collect_articles, 'comments': True},
	{'name': 'blog_post', 'verbose_name': "Blogy", 'fn': collect_blog_posts, 'comments': True},
	{'name': 'news', 'verbose_name': "Správy", 'fn': collect_news, 'comments': True},
	{'name': 'topic', 'verbose_name': "Fórum", 'fn': collect_topics, 'comments': True},
	{'name': 'tweet', 'verbose_name': "Tweety", 'fn': collect_tweets, 'comments': True},
]


def collect_activity(time_range: TimeRange):
	activity_sections = []

	for collector in COLLECTORS:
		context = collector.copy()

		collector_fn = context.pop('fn')

		items = collector_fn(time_range)
		if not items:
			continue

		if context.get('comments'):
			add_discussion_attributes({}, items)

		base_name = context['name']

		context['base_uri'] = get_base_uri()
		context[f'{base_name}_list'] = items
		context[f'item_list'] = items

		html_list_template = select_template([f'newsletter/{base_name}_list.html', 'newsletter/list.html'])
		html_item_template = select_template([f'newsletter/{base_name}_item.html', 'newsletter/item.html'])
		txt_list_template = select_template([f'newsletter/{base_name}_list.txt', 'newsletter/list.txt'])
		txt_item_template = select_template([f'newsletter/{base_name}_item.txt', 'newsletter/item.txt'])

		html_rendered_items = []
		txt_rendered_items = []
		for item in items:
			context['item'] = item
			context[base_name] = item
			html_rendered_items.append(html_item_template.render(context))
			txt_rendered_items.append(txt_item_template.render(context))

		del context['item']
		del context[base_name]

		context['rendered_item_list'] = html_rendered_items
		context[f'rendered_{base_name}_list'] = html_rendered_items
		html_rendered_content = html_list_template.render(context)

		context['rendered_item_list'] = txt_rendered_items
		context[f'rendered_{base_name}_list'] = txt_rendered_items
		txt_rendered_content = txt_list_template.render(context)

		activity_sections.append({
			'html': html_rendered_content,
			'txt': txt_rendered_content,
			'items': items,
		})

	return activity_sections


def send_weekly():
	activity = collect_activity(get_week_date_range())
	if not activity: # no updates, don't need to do anything
		return

	txt_content = ''.join(record['txt'] for record in activity)
	html_content = mark_safe('\n'.join(record['html'] for record in activity))

	# create title from individual item titles
	title = []
	title_length = 0
	has_more_items = False
	for section in activity:
		for item in section['items']:
			if title_length > 100:
				has_more_items = True
				break
			item = str(item)
			title.append(item)
			title_length += len(item) + 2

	current_date = date_format(timezone.localtime(timezone.now()), 'SHORT_DATE_FORMAT')
	title = ', '.join(title)
	if has_more_items:
		title = f'LinuxOS.sk: {title} …'
	title = f'{title} ({current_date})'
