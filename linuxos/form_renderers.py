# -*- coding: utf-8 -*-
from pathlib import Path

from django.forms import renderers
from django.utils.functional import cached_property


FORM_TEMPLATE_ROOT = Path(renderers.__file__).parent


class Jinja2(renderers.Jinja2):
	@cached_property
	def django_renderer(self):
		return renderers.DjangoTemplates()

	@cached_property
	def backend(self):
		from django.template.backends.jinja2 import Jinja2
		return Jinja2

	@cached_property
	def engine(self):
		backend = self.backend({
			'APP_DIRS': True,
			'DIRS': [FORM_TEMPLATE_ROOT / self.backend.app_dirname, Path(__file__).parent.parent / 'templates'],
			'NAME': 'djangoforms',
			'OPTIONS': {
				"environment": "template_dynamicloader.environment.Environment",
			},
		})
		from django_jinja.contrib._easy_thumbnails.templatetags.thumbnails import thumbnail, thumbnail_url
		backend.env.globals.update({
			'thumbnail_url': thumbnail_url,
			'thumbnail': thumbnail,
		})
		return backend

	def render(self, template_name, context, request=None):
		if template_name.startswith('admin/'):
			return self.django_renderer.render(template_name, context, request=request)
		else:
			return super().render(template_name, context, request=request)
