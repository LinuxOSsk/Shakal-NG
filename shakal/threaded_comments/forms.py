# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib.comments.forms import CommentForm, COMMENT_MAX_LENGTH
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelformset_factory
from django.forms.widgets import HiddenInput
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from attachment.fields import AttachmentField
from attachment.models import UploadSession, Attachment, TemporaryAttachment
from time import time
from models import ThreadedComment


class AttachmentForm(forms.Form):
	pass


AttachmentFormset = modelformset_factory(TemporaryAttachment, can_delete = True, extra = 0, fields = ())


class ThreadedCommentForm(CommentForm):
	subject = forms.CharField(label = _("Subject"), max_length = 100)
	parent_pk = forms.IntegerField(widget = forms.HiddenInput, required = False)
	comment = forms.CharField(label = _("Comment"), max_length = COMMENT_MAX_LENGTH, widget = forms.Textarea)
	attachment = AttachmentField(label = _("Attachment"), required = False)
	upload_session = forms.CharField(label = "Upload session", widget = HiddenInput, required = False)

	def __init__(self, *args, **kwargs):
		self.__parent_comment = kwargs.pop('parent_comment', None)
		logged = kwargs.pop('logged', False)
		files = kwargs.pop('files', {})
		super(ThreadedCommentForm, self).__init__(*args, **kwargs)
		self.files = files
		key_order = [
			'subject',
			'name',
			'comment',
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

		self.fields['attachment'].widget.attrs['max_size'] = TemporaryAttachment.get_available_size(ContentType.objects.get_for_model(ThreadedComment), -1, TemporaryAttachment)
		self.fields.keyOrder = key_order

	def process_attachments(self):
		if not self.files:
			return
		try:
			session = UploadSession.objects.get(uuid = self.data['upload_session'])
		except UploadSession.DoesNotExist:
			session = UploadSession()
			session.save()
		self.data['upload_session'] = session.uuid

		attachment = TemporaryAttachment(
			session = session,
			attachment = self.files['attachment'],
			content_type = ContentType.objects.get_for_model(TemporaryAttachment),
			object_id = session.id
		)
		attachment.save()

	def move_attachments(self, content_object):
		temp_attachments = self.get_attachments()
		if not temp_attachments:
			return
		for temp_attachment in temp_attachments:
			attachment = Attachment(
				attachment = temp_attachment.attachment.name,
				content_type = ContentType.objects.get_for_model(content_object.__class__),
				object_id = content_object.pk
			)
			attachment.save()
			temp_attachment.delete()

	def get_attachments(self):
		if self.data and 'upload_session' in self.data:
			try:
				session = UploadSession.objects.get(uuid = self.data['upload_session'])
				return TemporaryAttachment.objects.filter(session = session)
			except UploadSession.DoesNotExist:
				return []
		else:
			return []

	@property
	def attachments(self):
		if not hasattr(self, 'attachments_formset'):
			attachments = self.get_attachments()
			if self.data:
				self.attachments_formset = AttachmentFormset(queryset = attachments)
				rownum = 0
				while self.attachments_formset.prefix + '-' + str(rownum) + '-id' in self.data:
					pk = int(self.data[self.attachments_formset.prefix + '-' + str(rownum) + '-id'])
					if self.attachments_formset.prefix + '-' + str(rownum) + '-DELETE' in self.data:
						match = filter(lambda x: x.pk == pk, attachments)
						if match:
							match[0].delete()
					rownum += 1
				attachments = self.get_attachments()
			self.attachments_formset = AttachmentFormset(queryset = attachments)
		return self.attachments_formset

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
			'comment'   : self.data.get('comment'),
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
			'object_pk':    self.target_object._get_pk_val(),
			'user_name':    self.cleaned_data.get("name", ""),
			'user_url':     "",
			'comment':      self.cleaned_data["comment"],
			'submit_date':  timezone.now(),
			'site_id':      settings.SITE_ID,
			'is_public':    True,
			'is_removed':   False,
			'subject':      self.cleaned_data['subject'],
		}

	def clean_comment(self):
		data = self.cleaned_data['comment']
		return data
