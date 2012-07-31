from shakal.threaded_comments.models import ThreadedComment
from shakal.threaded_comments.forms import ThreadedCommentForm

def get_model():
	return ThreadedComment

def get_form():
	return ThreadedCommentForm
