# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from time import time

from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.forms.util import ErrorDict
from django.forms.widgets import HiddenInput
from django.utils.crypto import salted_hmac

from antispam.forms import AntispamFormMixin
from attachment.fields import AttachmentField
from attachment.forms import TemporaryAttachmentFormMixin
from common_utils import get_meta
from common_utils.middlewares.ThreadLocal import get_current_request
from rich_editor.forms import RichOriginalField
from threaded_comments.models import Comment


COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 50000)


class SecurityFormMixin(object):
	timestamp = forms.IntegerField(widget=forms.HiddenInput)
	security_hash = forms.CharField(min_length=40, max_length=40, widget=forms.HiddenInput)
	honeypot = forms.CharField(required=False, label='Ak do tohto poľa niečo napíšete bude príspevok pvažovaný za spam.')

	def generate_security_data(self):
		security_dict = {
			'timestamp': int(time())
		}
		security_dict.update(self.additional_security_data())
		security_dict['security_hash'] = self.generate_security_hash(security_dict)
		return security_dict

	def additional_security_data(self):
		return {}

	def generate_security_hash(self, security_dict):
		key_salt = 'secutity_form'
		value = '-'.join(str(v) for v in security_dict.values())
		return salted_hmac(key_salt, value).hexdigest()

	def security_errors(self):
		errors = ErrorDict()
		for f in ['timestamp', 'security_hash']:
			if f in self.errors:
				errors[f] = self.errors[f]
		return errors

	def clean_honeypot(self):
		value = self.cleaned_data["honeypot"]
		if value:
			raise forms.ValidationError(self.fields["honeypot"].label)
		return value

	def clean_timestamp(self):
		ts = self.cleaned_data['timestamp']
		if time() - ts > (2 * 60 * 60):
			raise forms.ValidationError('Timestamp check failed')
		return ts

	def clean_security_hash(self):
		security_dict = self.generate_security_data()
		del security_dict['security_hash']
		expected_hash = self.generate_security_hash(security_dict)
		actual_hash = self.cleaned_data['security_hash']
		if not expected_hash == actual_hash:
			raise forms.ValidationError('Security hash check failed.')
		return actual_hash


class CommentForm(SecurityFormMixin, TemporaryAttachmentFormMixin, AntispamFormMixin, forms.ModelForm):
	original_comment = RichOriginalField(
		parsers=get_meta(Comment).get_field('original_comment').parsers,
		label='Komentár',
		validators=[validators.MaxLengthValidator(COMMENT_MAX_LENGTH)]
	)

	attachment = AttachmentField(label='Príloha', required=False)
	upload_session = forms.CharField(widget=HiddenInput, required=False)

	class Meta:
		model = Comment
		fields = [
			'content_type',
			'object_id',
			'parent',
			'subject',
			'user_name',
			'original_comment'
		]
		widgets = {
			'content_type': forms.HiddenInput,
			'object_id': forms.HiddenInput,
			'parent': forms.HiddenInput,
		}

	def __init__(self, target_object, parent_id, data=None, initial=None, *args, **kwargs):
		self.parent_id = parent_id
		self.target_object = target_object
		initial = initial or {}
		initial.update(self.generate_security_data())
		super(CommentForm, self).__init__(data=data, initial=initial, *args, **kwargs)
		self.fields['parent'].required = True
		self.request = get_current_request()
		if self.request.user.is_authenticated():
			del self.fields['user_name']
		else:
			self.fields['user_name'].required = True
		self.process_attachments()

	def get_model(self):
		return Comment

	def get_comment_object(self):
		if self.is_valid():
			return self.save(commit=False)
		else:
			return None

	def additional_security_data(self):
		return {
			'parent': self.parent_id,
			'object_id': self.target_object.pk,
			'content_type': ContentType.objects.get_for_model(self.target_object).pk,
		}

	def check_for_duplicate_comment(self, new):
		possible_duplicates = Comment.objects.filter(
			content_type=new.content_type,
			object_id=new.object_id,
			user_name=new.user_name,
		)
		for old in possible_duplicates:
			if old.submit_date.date() == new.submit_date.date() and old.original_comment == new.original_comment:
				return old
		return new
