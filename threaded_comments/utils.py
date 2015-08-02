# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import CommentFlag


def perform_flag_action(request, comment, comment_flag, action=None):
	flag, created = CommentFlag.objects.get_or_create(
		comment=comment,
		user=request.user,
		flag=comment_flag
	)
	if action:
		action(comment)
	signals.comment_was_flagged.send(
		sender=comment.__class__,
		comment=comment,
		flag=flag,
		created=created,
		request=request
	)


def perform_flag(request, comment):
	perform_flag_action(request, comment, CommentFlag.SUGGEST_REMOVAL)


def perform_delete(request, comment):
	def action(comment):
		comment.is_removed = True
		comment.save()
	perform_flag_action(request, comment, CommentFlag.MODERATOR_DELETION, action)


def perform_approve(request, comment):
	def action(comment):
		comment.is_removed = False
		comment.is_public = True
		comment.save()
	perform_flag_action(request, comment, CommentFlag.MODERATOR_APPROVAL, action)
