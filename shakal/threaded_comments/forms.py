# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib.comments.forms import CommentForm, COMMENT_MAX_LENGTH
from django.contrib.contenttypes.models import ContentType
from django.forms.widgets import HiddenInput
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from antispam.forms import AntispamFormMixin
from attachment.fields import AttachmentField
from attachment.forms import AttachmentFormMixin
from html_editor.fields import HtmlField
from time import time
from models import ThreadedComment


class ThreadedCommentForm(CommentForm, AttachmentFormMixin, AntispamFormMixin):
	subject = forms.CharField(label = _("Subject"), max_length = 100)
	parent_pk = forms.IntegerField(widget = forms.HiddenInput, required = False)
	comment = HtmlField(label = _("Comment"), max_length = COMMENT_MAX_LENGTH)
	attachment = AttachmentField(label = _("Attachment"), required = False)
	upload_session = forms.CharField(label = "Upload session", widget = HiddenInput, required = False)

	def __init__(self, *args, **kwargs):
		self.__parent_comment = kwargs.pop('parent_comment', None)
		logged = kwargs.pop('logged', False)
		files = kwargs.pop('files', {})
		request = kwargs.pop('request')
		super(ThreadedCommentForm, self).__init__(*args, **kwargs)
		self.files = files
		key_order = [
			'subject',
			'name',
			'comment',
			'captcha',
			'attachment',
			'honeypot',
			'content_type',
			'object_pk',
			'timestamp',
			'security_hash',
			'parent_pk',
			'upload_session'
		]
		del self.fields['url']
		if logged:
			del self.fields['name']
			del key_order[1]
			del self.fields['captcha']
			del key_order[2]

		self.fields.keyOrder = key_order
		self.process_antispam(request)
		self.process_attachments()

	def get_model(self):
		return ThreadedComment

	def get_comment_model(self):
		return ThreadedComment

	def get_comment_object(self):
		comment = super(ThreadedCommentForm, self).get_comment_object()
		parent_pk = self.cleaned_data.get('parent_pk')
		parent_comment = ThreadedComment.objects.get(pk = parent_pk)
		comment.subject  = self.cleaned_data['subject']
		comment.parent = parent_comment
		return comment

	def get_comment_dict(self):
		return {
			'subject'   : self.data.get('subject'),
			'user_name' : self.data.get('name'),
			'email'     : self.data.get('email'),
			'url'       : self.data.get('url'),
			'comment'   : self.fields['comment'].to_python(self.data.get('comment')),
			'is_public' : True,
			'is_removed': False,
		}

	def generate_security_data(self):
		timestamp = int(time())
		security_dict =   {
			'content_type'  : str(self.target_object._meta),
			'object_pk'     : str(self.target_object._get_pk_val()),
			'parent_pk'     : str(self.__parent_comment.pk),
			'timestamp'     : str(timestamp),
			'security_hash' : self.initial_security_hash(timestamp),
		}
		return security_dict

	def get_comment_create_data(self):
		return {
			'content_type': ContentType.objects.get_for_model(self.target_object),
			'object_pk'   : self.target_object._get_pk_val(),
			'user_name'   : self.cleaned_data.get("name", ""),
			'user_url'    : "",
			'comment'     : self.cleaned_data["comment"],
			'submit_date' : timezone.now(),
			'site_id'     : settings.SITE_ID,
			'subject'     : self.cleaned_data['subject'],
		}

	def clean_comment(self):
		data = self.cleaned_data['comment']
		return data
