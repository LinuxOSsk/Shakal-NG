# -*- coding: utf-8 -*-
from time import time

from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.forms.util import ErrorDict
from django.forms.widgets import HiddenInput
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.utils.translation import ugettext_lazy as _

from antispam.forms import AntispamFormMixin
from attachment.fields import AttachmentField
from attachment.forms import AttachmentFormMixin
from rich_editor.forms import RichOriginalField
from threaded_comments.models import Comment


COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class CommentForm(AttachmentFormMixin, AntispamFormMixin, forms.Form):
	content_type = forms.CharField(widget=forms.HiddenInput)
	object_id = forms.CharField(widget=forms.HiddenInput)
	timestamp = forms.IntegerField(widget=forms.HiddenInput)
	security_hash = forms.CharField(min_length = 40, max_length = 40, widget=forms.HiddenInput)
	parent_pk = forms.IntegerField(widget = forms.HiddenInput, required = False)
	upload_session = forms.CharField(widget = HiddenInput, required = False)
	honeypot = forms.CharField(required = False, label=_('If you enter anything in this field your comment will be treated as spam'))

	name = forms.CharField(label = _("Name"), max_length = 50)
	subject = forms.CharField(label = _("Subject"), max_length = 100)
	original_comment = RichOriginalField(label = _("Comment"), max_length = COMMENT_MAX_LENGTH)
	attachment = AttachmentField(label = _("Attachment"), required = False)

	def __init__(self, target_object, data = None, initial = None, *args, **kwargs):
		self.parent_comment = kwargs.pop('parent_comment', None)
		self.target_object = target_object
		if initial is None:
			initial = {}
		initial.update(self.generate_security_data())
		logged = kwargs.pop('logged', False)
		request = kwargs.pop('request')
		super(CommentForm, self).__init__(data = data, initial = initial, *args, **kwargs)
		key_order = [
			'subject',
			'name',
			'original_comment',
			'captcha',
			'attachment',
			'honeypot',
			'content_type',
			'object_id',
			'timestamp',
			'security_hash',
			'parent_pk',
			'upload_session'
		]
		if logged:
			del self.fields['name']
			del key_order[1]
			del self.fields['captcha']
			del key_order[2]

		self.fields.keyOrder = key_order
		self.process_antispam(request)
		self.process_attachments()

	def get_model(self):
		return Comment

	def security_errors(self):
		errors = ErrorDict()
		for f in ["honeypot", "timestamp", "security_hash"]:
			if f in self.errors:
				errors[f] = self.errors[f]
		return errors

	def clean_security_hash(self):
		security_hash_dict = {
			'content_type': self.data.get("content_type", ""),
			'object_id': self.data.get("object_id", ""),
			'timestamp': self.data.get("timestamp", ""),
		}
		expected_hash = self.generate_security_hash(**security_hash_dict)
		actual_hash = self.cleaned_data["security_hash"]
		if not expected_hash == actual_hash:
			raise forms.ValidationError("Security hash check failed.")
		return actual_hash

	def clean_timestamp(self):
		ts = self.cleaned_data["timestamp"]
		if time() - ts > (2 * 60 * 60):
			raise forms.ValidationError("Timestamp check failed")
		return ts

	def get_comment_object(self):
		if not self.is_valid():
			raise ValueError("get_comment_object may only be called on valid forms")
		comment = self.get_model()(**self.get_comment_create_data())
		comment = self.check_for_duplicate_comment(comment)
		parent_pk = self.cleaned_data.get('parent_pk')
		parent_comment = Comment.all_comments.get(pk = parent_pk)
		comment.subject = self.cleaned_data['subject']
		comment.parent = parent_comment
		return comment

	def get_comment(self):
		comment = Comment(
			subject = self.data.get('subject'),
			user_name = self.data.get('name'),
			is_public = True,
			is_removed = False,
		)
		comment.original_comment = (self.data.get('original_comment_format'), self.data.get('original_comment'))
		return comment

	def generate_security_data(self):
		timestamp = int(time())
		security_dict = {
			'content_type':   str(self.target_object._meta),
			'object_id':      str(self.target_object._get_pk_val()),
			'parent_pk':      str(self.parent_comment.pk),
			'timestamp':      str(timestamp),
			'security_hash':  self.initial_security_hash(timestamp),
		}
		return security_dict

	def initial_security_hash(self, timestamp):
		initial_security_dict = {
			'content_type': str(self.target_object._meta),
			'object_id': str(self.target_object._get_pk_val()),
			'timestamp': str(timestamp),
		}
		return self.generate_security_hash(**initial_security_dict)

	def generate_security_hash(self, content_type, object_id, timestamp):
		info = (content_type, object_id, timestamp)
		key_salt = "threaded_comments.forms.CommentForm"
		value = "-".join(info)
		return salted_hmac(key_salt, value).hexdigest()

	def get_comment_create_data(self):
		return {
			'content_type':     ContentType.objects.get_for_model(self.target_object),
			'object_id':        self.target_object._get_pk_val(),
			'user_name':        self.cleaned_data.get("name", ""),
			'original_comment': self.cleaned_data["original_comment"],
			'submit_date':      timezone.now(),
			'subject':          self.cleaned_data['subject'],
		}

	def check_for_duplicate_comment(self, new):
		possible_duplicates = self.get_model().objects.filter(
			content_type = new.content_type,
			object_id = new.object_id,
			user_name = new.user_name,
		)
		for old in possible_duplicates:
			if old.submit_date.date() == new.submit_date.date() and old.original_comment == new.original_comment:
				return old
		return new

	def clean_honeypot(self):
		value = self.cleaned_data["honeypot"]
		if value:
			raise forms.ValidationError(self.fields["honeypot"].label)
		return value
