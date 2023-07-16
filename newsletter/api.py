# -o- coding: utf-8 -*-
import base64
import logging
import sys
from datetime import timedelta, time, datetime, date
from itertools import chain
from typing import Tuple, Optional, List

from django.conf import settings
from django.core import signing
from django.core.mail import EmailMultiAlternatives
from django.template import engines
from django.template.loader import select_template, render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.safestring import mark_safe

from .models import NewsletterSubscription, MassEmailExclude
from article.models import Article
from blog.models import Post
from comments.templatetags.comments_tags import add_discussion_attributes
from desktops.models import Desktop
from forum.models import Topic
from linuxos.templatetags.linuxos import get_base_uri
from news.models import News
from tweets.models import Tweet


logger = logging.getLogger(__name__)
SALT = 'newsletter_subscription'
SENDING_HOUR = 8
TimeRange = Tuple[datetime, datetime]


def get_week_date_range(today: Optional[date] = None) -> TimeRange:
	if today is None:
		today = timezone.now().date()
		week_start = today - timedelta(days=today.weekday() + 7)
	else:
		week_start = today - timedelta(days=today.weekday())
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


def collect_desktops(time_range: Desktop):
	return filter_range(Desktop.objects
		.order_by('created'), time_range, 'created')[:200]


COLLECTORS = [
	{'name': 'article', 'verbose_name': "Články", 'fn': collect_articles, 'comments': True},
	{'name': 'blog_post', 'verbose_name': "Blogy", 'fn': collect_blog_posts, 'comments': True},
	{'name': 'news', 'verbose_name': "Správy", 'fn': collect_news, 'comments': True},
	{'name': 'topic', 'verbose_name': "Fórum", 'fn': collect_topics, 'comments': True},
	{'name': 'tweet', 'verbose_name': "Tweety", 'fn': collect_tweets, 'comments': True},
	{'name': 'desktop', 'verbose_name': "Desktop", 'fn': collect_desktops, 'comments': True},
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


def render_weekly(today: Optional[date] = None):
	date_range = get_week_date_range(today)
	today = (date_range[1] - timedelta(hours=SENDING_HOUR) - timedelta(seconds=1)).date()

	activity = collect_activity(date_range)
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

	web_link = get_base_uri() + reverse('newsletter:weekly_newsletter', kwargs={'format': 'html', 'date': today.strftime('%Y-%m-%d')})
	context = {'title': title, 'content': txt_content, 'newsletter_date': date_range[1]}
	txt_data = render_to_string('newsletter/email/message.txt', context)
	context['content'] = html_content
	html_data = render_to_string('newsletter/email/message.html', context)

	return {
		'title': title,
		'txt_data': txt_data,
		'html_data': html_data,
		'html_content': html_content,
		'txt_content': txt_content,
		'web_link': web_link,
		'newsletter_date': date_range[1],
	}


def unsign_email(email: str) -> Optional[str]:
	try:
		email = signing.Signer(salt=SALT).unsign(email)
		return base64.urlsafe_b64decode(email.encode('utf-8')).decode('utf-8')
	except signing.BadSignature:
		pass


def sign_email(email: str) -> str:
	email = base64.urlsafe_b64encode(email.encode('utf-8')).decode('utf-8')
	return signing.Signer(salt=SALT).sign(email)


def send_weekly(recipients: Optional[List[str]] = None):
	weekly_news = render_weekly()
	if not weekly_news:
		return

	dummy_recipient = 'subscribers@linuxos.sk'
	if recipients is None:
		recipients = (NewsletterSubscription.objects
			.exclude(email=dummy_recipient)
			.values_list('email', flat=True))
		chain(recipients, [dummy_recipient])

	sent = 0

	for recipient in recipients:
		try:
			email_token = sign_email(recipient)
			unsubscribe_link = get_base_uri() + reverse('newsletter:unsubscribe', kwargs={'token': email_token})
			context = {
				'title': weekly_news['title'],
				'content': weekly_news['txt_content'],
				'newsletter_date': weekly_news['newsletter_date'],
				'web_link': weekly_news['web_link'],
				'unsubscribe_link': unsubscribe_link,
			}
			txt_data = render_to_string('newsletter/email/message.txt', context)
			context['content'] = weekly_news['html_content']
			html_data = render_to_string('newsletter/email/message.html', context)

			msg = EmailMultiAlternatives(
				subject=context['title'],
				body=txt_data,
				from_email=settings.DEFAULT_FROM_EMAIL,
				to=[recipient],
				headers={
					'List-Unsubscribe': f'<{unsubscribe_link}>',
					'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
				},
			)
			if sent > 0: # save only first
				msg.model_instance = None
			msg.attach_alternative(html_data, 'text/html')
			msg.send()
			sent += 1
		except Exception:
			logger.exception("Failed to send newsletter e-mail")


def send_mass_email(
	recipients: List[str],
	subject_template: str,
	txt_message_template: str,
	html_message_template: str
):
	default_template_engine = engines.all()[0]

	excludes = set(MassEmailExclude.objects.values_list('email', flat=True))
	recipients = [recipient for recipient in recipients if recipient not in excludes]

	subject_template_instance = default_template_engine.from_string(subject_template)
	txt_message_template_instance = default_template_engine.from_string(txt_message_template)
	html_message_template_instance = default_template_engine.from_string(html_message_template)

	sent = 0

	ctx = {'base_uri': get_base_uri()}
	for recipient in recipients:
		ctx['email'] = recipient
		subject = subject_template_instance.render(ctx)
		txt_message = txt_message_template_instance.render(ctx)
		html_message = html_message_template_instance.render(ctx)

		status = 0
		try:
			msg = EmailMultiAlternatives(
				subject=subject,
				body=txt_message,
				from_email=settings.DEFAULT_FROM_EMAIL,
				to=[recipient],
			)
			msg.attach_alternative(html_message, 'text/html')
			if sent > 0: # save only first
				msg.model_instance = None
			status = msg.send()
			status_text = 'OK' if status else 'ERR'
			sent += 1
			sys.stdout.write(f'{status_text} {recipient}\n')
		except Exception:
			logger.warning("E-mail not sent to %s", recipient, exc_info=True)
		else:
			if not status:
				logger.warning("E-mail not sent to %s", recipient)
