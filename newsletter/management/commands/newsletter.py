# -*- coding: utf-8 -*-
import argparse
import sys
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db.models import Subquery, OuterRef, Count, Value as V, F
from django.db.models.functions import Coalesce
from django.utils import timezone

from ...api import send_weekly, send_mass_email, import_excludes
from article.models import Article
from comments.models import Comment
from common_utils.argparse import add_subparsers
from news.models import News
from tweets.models import Tweet


User = get_user_model()


class Command(BaseCommand):
	def add_arguments(self, parser):
		subparsers = add_subparsers(self, parser, description="Subcommand", required=True)
		subparsers.dest = 'subcommand'
		subparsers.add_parser("send_weekly")
		parser = subparsers.add_parser("send_mass")
		parser.add_argument('recipient_list', type=argparse.FileType(mode='r'))
		parser.add_argument('subject_template', type=str)
		parser.add_argument('txt_message_template', type=argparse.FileType(mode='r'))
		parser.add_argument('html_message_template', type=argparse.FileType(mode='r'))
		parser = subparsers.add_parser("list_active_users")
		parser.add_argument('min_weight', type=int)
		parser.add_argument('--show_weight', action='store_true')
		parser = subparsers.add_parser("import_excludes")
		parser.add_argument('excludes', type=argparse.FileType(mode='r'))

	def handle(self, *args, **options):
		subcommand = options.pop('subcommand')
		return getattr(self, subcommand)(**options)

	def send_weekly(self, **options): # pylint: disable=unused-argument
		send_weekly()

	def send_mass(self, **options):
		recipients = [address.strip() for address in options['recipient_list'] if address.strip()]
		txt_message_template = options['txt_message_template'].read()
		html_message_template = options['html_message_template'].read()
		send_mass_email(
			recipients,
			subject_template=options['subject_template'],
			txt_message_template=txt_message_template,
			html_message_template=html_message_template
		)

	def list_active_users(self, **options):
		now = timezone.now()
		recent_range = [now, now - timedelta(days=365)]
		old_range = [now - timedelta(days=365), now - timedelta(days=365*3)]
		extraold_range = [now - timedelta(days=365 * 3), now - timedelta(days=365*50)]

		def annotate_count(qs, author_field, date_range):
			filters = {
				author_field: OuterRef('pk'),
				'created__gte': date_range[1],
				'created__lt': date_range[0]
			}
			return Coalesce(Subquery(qs
				.filter(**filters)
				.annotate(x=V('x'))
				.values('x')
				.order_by('x')
				.annotate(cnt=Count('x'))
				.values('cnt')[:1]
			), V(0))

		users = (User.objects
			.annotate(
				recent_articles=annotate_count(Article.objects.all(), 'author_id', recent_range),
				old_articles=annotate_count(Article.objects.all(), 'author_id', old_range),
				extraold_articles=annotate_count(Article.objects.all(), 'author_id', extraold_range),
				recent_news=annotate_count(News.objects.all(), 'author_id', recent_range),
				old_news=annotate_count(News.objects.all(), 'author_id', old_range),
				extraold_news=annotate_count(News.objects.all(), 'author_id', extraold_range),
				recent_tweets=annotate_count(Tweet.objects.all(), 'author_id', recent_range),
				old_tweets=annotate_count(Tweet.objects.all(), 'author_id', old_range),
				extraold_tweets=annotate_count(Tweet.objects.all(), 'author_id', extraold_range),
				recent_comments=annotate_count(Comment.objects.order_by('id'), 'user_id', recent_range),
				old_comments=annotate_count(Comment.objects.order_by('id'), 'user_id', old_range),
				extraold_comments=annotate_count(Comment.objects.order_by('id'), 'user_id', extraold_range),
			)
		)

		weights = {
			'news': 10,
			'tweets': 5,
			'articles': 200,
		}

		total_weight = F('recent_comments') * 50 + F('old_comments') * 10 + F('extraold_comments')
		for field, weight in weights.items():
			total_weight = total_weight + (F(f'recent_{field}') * 50 + F(f'old_{field}') * 10 + F(f'extraold_{field}')) * weight

		users = (users
			.annotate(total_weight=total_weight)
			.filter(total_weight__gte=options['min_weight'])
			.exclude(email='')
			.values_list('total_weight', 'email'))

		for weight, email in users:
			if options['show_weight']:
				sys.stdout.write(f'{weight} {email}\n')
			else:
				sys.stdout.write(f'{email}\n')

	def import_excludes(self, **options):
		excludes = [address.strip() for address in options['excludes'] if address.strip()]
		import_excludes(excludes)
