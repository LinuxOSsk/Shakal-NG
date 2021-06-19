# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string, TemplateDoesNotExist

from common_utils import build_absolute_uri


def get_site_base():
	return {
		'base_uri': build_absolute_uri('')
	}


def create_html_mail(subject, body, to, from_email=None, html_body=None, **kwargs):
	msg = EmailMultiAlternatives(subject=subject, body=body, from_email=from_email, to=to, **kwargs)
	if html_body is not None:
		msg.attach_alternative(html_body, 'text/html')
	return msg


def create_template_mail(template_base, context, to, from_email=None, **kwargs):
	context = context.copy()
	context.update(get_site_base())
	from_email = from_email or settings.DEFAULT_FROM_EMAIL
	subject = render_to_string(template_base + '_subject.txt', context).strip()
	body = render_to_string(template_base + '_message.txt', context)
	try:
		html_body = render_to_string(template_base + '_message.html', context)
	except TemplateDoesNotExist:
		html_body = None
	msg = create_html_mail(subject=subject, body=body, from_email=from_email, to=to, html_body=html_body, **kwargs)
	return msg


def send_template_mail(*args, **kwargs):
	msg = create_template_mail(*args, **kwargs)
	msg.send()
