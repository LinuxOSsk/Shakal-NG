# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys

from collections import OrderedDict
from compressor.cache import get_offline_hexdigest, write_offline_manifest
from compressor.exceptions import TemplateSyntaxError, TemplateDoesNotExist
from django.conf import settings
from django.core.management.base import CommandError, BaseCommand
from django.template import Context


class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		templates = self.__get_templates()
		nodes = self.__parse_templates(templates)
		self.__compress_nodes(nodes)

	def __get_templates(self):
		template_dir = settings.TEMPLATES[0]['DIRS'][0]
		templates = set()
		for root, _, files in os.walk(template_dir):
			for filename in files:

				if not '.compress.' in  filename:
					continue
				templates.add(os.path.join(root, filename))
		return templates

	def __get_parser(self):
		from compressor.offline.jinja2 import Jinja2Parser
		env = settings.COMPRESS_JINJA2_GET_ENVIRONMENT()
		parser = Jinja2Parser(charset=settings.FILE_CHARSET, env=env)
		return parser

	def __parse_templates(self, templates):
		parser = self.__get_parser()
		log = sys.stdout

		compressor_nodes = OrderedDict()
		for template_name in templates:
			try:
				template = parser.parse(template_name)
			except IOError:  # unreadable file -> ignore
				log.write("Unreadable template at: %s\n" % template_name)
				continue
			except TemplateSyntaxError as e:  # broken template -> ignore
				log.write("Invalid template %s: %s\n" % (template_name, e))
				continue
			except TemplateDoesNotExist:  # non existent template -> ignore
				log.write("Non-existent template at: %s\n" % template_name)
				continue
			except UnicodeDecodeError:
				log.write("UnicodeDecodeError while trying to read template %s\n" % template_name)
			try:
				nodes = list(parser.walk_nodes(template))
			except (TemplateDoesNotExist, TemplateSyntaxError) as e:
				# Could be an error in some base template
				log.write("Error parsing template %s: %s\n" % (template_name, e))
				continue
			if nodes:
				template.template_name = template_name
				compressor_nodes.setdefault(template, []).extend(nodes)
		return compressor_nodes

	def __compress_nodes(self, compressor_nodes):
		parser = self.__get_parser()
		offline_manifest = OrderedDict()
		init_context = parser.get_init_context(settings.COMPRESS_OFFLINE_CONTEXT)

		for template, nodes in compressor_nodes.items():
			#template._log = sys.stdout
			#template._log_verbosity = 1

			if not parser.process_template(template, init_context):
				continue

			for node in nodes:
				parser.process_node(template, init_context, node)
				rendered = parser.render_nodelist(template, init_context, node)
				key = get_offline_hexdigest(rendered)

				if key in offline_manifest:
					continue

				try:
					result = parser.render_node(template, init_context, node)
				except Exception as e:
					raise CommandError("An error occured during rendering %s: %s" % (template.template_name, e))
				offline_manifest[key] = result

		write_offline_manifest(offline_manifest)
