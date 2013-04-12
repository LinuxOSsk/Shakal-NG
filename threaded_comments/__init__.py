from threaded_comments.models import Comment
from threaded_comments.forms import CommentForm


def get_model():
	return Comment


def get_form():
	return CommentForm
