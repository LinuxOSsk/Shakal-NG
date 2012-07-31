# -*- coding: utf-8 -*-

from django import forms
from django.contrib.comments.forms import CommentForm, COMMENT_MAX_LENGTH
from django.utils.translation import ugettext_lazy as _

class ThreadedCommentForm(CommentForm):
	subject = forms.CharField(max_length = 100),
	url = forms.URLField(widget = forms.HiddenInput, required = False),
	parent_pk = forms.IntegerField(widget = forms.HiddenInput, required = False),
	comment = forms.CharField(label = _("Comment"), max_length = COMMENT_MAX_LENGTH)

	def __init__(self, *args, **kwargs):
		self.__parent_comment = kwargs.pop('parent_comment', None)
		super(ThreadedCommentForm, self).__init__(*args, **kwargs)
		self.fields.keyOrder = [
			'subject',
			'name',
			'url',
			'comment',
			'honeypot',
			'content_type',
			'object_pk',
			'timestamp',
			'security_hash',
			'parent_pk'
		]
