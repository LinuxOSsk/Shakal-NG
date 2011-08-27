from threaded_comments.models import ThreadedComment
from threaded_comments.forms import ThreadedCommentForm
from django.core import urlresolvers

def get_model():
	return ThreadedComment

def get_form():
	return ThreadedCommentForm

def get_form_target():
	return urlresolvers.reverse('post-comment')

