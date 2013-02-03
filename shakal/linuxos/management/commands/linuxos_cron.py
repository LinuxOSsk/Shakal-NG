# -*- coding: utf-8 -*-

from attachment.models import TemporaryAttachment
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.db.models import Count
from shakal.accounts.models import UserRating

class Command(BaseCommand):
	args = ''
	help = 'Cron'

	def __init__(self, *args, **kwargs):
		super(Command, self).__init__(*args, **kwargs)

	def handle(self, *args, **kwargs):
		self.delete_old_attachments()
		self.update_user_ratings()

	def delete_old_attachments(self):
		now = datetime.datetime.now()
		old_date = now - datetime.timedelta(days = 1)
		old_attachments = TemporaryAttachment.objects.filter(created__lt = old_date)[:]
		for old_attachment in old_attachments:
			old_attachment.delete()

	def update_user_ratings(self):
		columns = (
			'user',
			'comments',
			'articles',
			'helped',
			'news',
			'wiki'
		)
		ratings = UserRating.objects.values_list(*columns)
		ratings = [dict(zip(columns, r)) for r in ratings]
		ratings = dict([(r['user'], r) for r in ratings])

		user_comments = User.objects.extra(
			{'num_comments':
				'SELECT COUNT(*) \
					FROM django_comments \
					WHERE \
						auth_user.id = django_comments.user_id AND \
						django_comments.is_public AND \
						NOT django_comments.is_removed'}
			).values_list('id', 'num_comments')
		user_comments_changed = filter(lambda c: c[0] not in ratings or c[1] != ratings[c[0]]['comments'], user_comments)
		for user_id, comment_count in user_comments_changed:
			rating, created = UserRating.objects.get_or_create(user_id = user_id)
			rating.comments = comment_count
			rating.save()
