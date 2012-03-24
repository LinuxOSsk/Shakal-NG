# -*- coding: utf-8 -*-
from django import http
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.comments.views.utils import next_redirect, confirmation_view
from django.contrib.comments import signals
from shakal.threaded_comments.models import ThreadedComment
from shakal.threaded_comments import get_form

class CommentPostBadRequest(http.HttpResponseBadRequest):
	def __init__(self, why):
		super(CommentPostBadRequest, self).__init__()
		if settings.DEBUG:
			self.content = render_to_string("comments/400-debug.html", {'why': why})

def new_comment(request, comment_id):
	""" Dialóg pre pridanie nového komentára. """
	parent_comment = ThreadedComment.objects.get(pk = comment_id)
	content_object = parent_comment.content_object
	form = get_form()(content_object, parent_comment)

	model_meta = content_object.__class__._meta
	template_list = [
		"comments/{0}_{1}_new_form.html".format(*tuple(str(model_meta).split('.'))),
		"comments/{0}_new_form.html".format(model_meta.app_label),
		"comments/new_form.html",
	]
	return render_to_response(template_list, {'form': form, 'next': content_object.get_absolute_url() }, RequestContext(request, {}))

@csrf_protect
@require_POST
def post_comment(request, next = None, using = None):
	""" Odoslanie komentára. """
	data = request.POST.copy()
	next = data.get('next', next)
	if request.user.is_authenticated():
		if not data.get('name', ''):
			data['name'] = request.user.get_full_name() or request.user.username
		if not data.get('email', ''):
			data['email'] = request.user.email
	if not data.get('email', ''):
		data['email'] = 'no@user.no'


	# Look up the object we're trying to comment about
	ctype = data.get("content_type")
	object_pk = data.get("object_pk")
	parent_pk = data.get("parent_pk")
	parent = None
	if ctype is None:
		return CommentPostBadRequest("Missing content_type field.")
	if object_pk is None:
		return CommentPostBadRequest("Missing object_pk field.")
	if parent_pk is None:
		return CommentPostBadRequest("Missing parent_pk field.")
	try:
		model = models.get_model(*ctype.split(".", 1))
		target = model._default_manager.using(using).get(pk=object_pk)
		parent = ThreadedComment.objects.get(pk = parent_pk)
	except TypeError:
		return CommentPostBadRequest(
			"Invalid content_type value: %r" % escape(ctype))
	except AttributeError:
		return CommentPostBadRequest(
			"The given content-type %r does not resolve to a valid model." % \
				escape(ctype))
	except ObjectDoesNotExist:
		return CommentPostBadRequest(
			"No object matching content-type %r and object PK %r exists." % \
				(escape(ctype), escape(object_pk)))
	except (ValueError, ValidationError), e:
		return CommentPostBadRequest(
			"Attempting go get content-type %r and object PK %r exists raised %s" % \
				(escape(ctype), escape(object_pk), e.__class__.__name__))

	preview = 'preview' in data
	form = get_form()(target, parent_comment = parent, data = data)

	# Check security information
	if form.security_errors():
		return CommentPostBadRequest(
			"The comment form failed security verification: %s" % \
				escape(str(form.security_errors())))

	# If there are errors or if we requested a preview show the comment
	if form.errors or preview:
		template_list = [
			"comments/{0}_{1}_preview.html".format(model._meta.app_label, model._meta.module_name),
			"comments/{0}_preview.html".format(model._meta.app_label),
			"comments/preview.html",
		]
		return render_to_response(
			template_list, {
				"comment" : form.get_comment_dict(),
				"form" : form,
				"next": next,
			},
			RequestContext(request, {})
		)

	comment = form.get_comment_object()
	comment.ip_address = request.META.get("REMOTE_ADDR", None)
	if request.user.is_authenticated():
		comment.user = request.user

	# Signal that the comment is about to be saved
	responses = signals.comment_will_be_posted.send (
		sender  = comment.__class__,
		comment = comment,
		request = request
	)

	for (receiver, response) in responses:
		if response == False:
			return CommentPostBadRequest(
				"comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

	# Save the comment and signal that it was saved
	comment.save()
	signals.comment_was_posted.send(
		sender  = comment.__class__,
		comment = comment,
		request = request
	)

	return next_redirect(data, next, 'done-comment', c=comment._get_pk_val())

done_comment = confirmation_view (
	template = "comments/posted.html",
	doc = """Display a "comment was posted" success page."""
)

