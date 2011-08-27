from django import forms
from django.contrib.comments.forms import CommentForm
from django.utils.translation import ugettext_lazy as _
from models import ThreadedComment
import time

class ThreadedCommentForm(CommentForm):
	title = forms.CharField(max_length = 100)
	url = forms.URLField(widget = forms.HiddenInput, required = False)
	parent_pk = forms.IntegerField(widget = forms.HiddenInput, required = False)
	email = forms.EmailField(widget = forms.HiddenInput, label=_("Email address"), required=False)

	def __init__(self, target_object, parent_comment=None, data=None, initial=None):
		self.parent_comment = parent_comment
		super(ThreadedCommentForm, self).__init__(target_object, data=data, initial=initial)
		self.fields.keyOrder = [
			'title',
			'name',
			'email',
			'url',
			'comment',
			'honeypot',
			'content_type',
			'object_pk',
			'timestamp',
			'security_hash',
			'parent_pk'
		]

	def get_comment_model(self):
		return ThreadedComment

	def get_comment_object(self):
		comment = super(ThreadedCommentForm, self).get_comment_object()
		parent_pk = self.cleaned_data.get('parent_pk')
		parent_comment = ThreadedComment.objects.get(pk = parent_pk)
		comment.title  = self.cleaned_data['title']
		comment.parent = parent_comment
		return comment

	def generate_security_data(self):
		timestamp = int(time.time())
		security_dict =   {
			'content_type'  : str(self.target_object._meta),
			'object_pk'     : str(self.target_object._get_pk_val()),
			'parent_pk'     : str(self.parent_comment.pk),
			'timestamp'     : str(timestamp),
			'security_hash' : self.initial_security_hash(timestamp),
		}
		return security_dict

	def get_comment_create_data(self):
		data = super(ThreadedCommentForm, self).get_comment_create_data()
		data['title'] = self.cleaned_data['title']
		data['url'] = ''
		return data

