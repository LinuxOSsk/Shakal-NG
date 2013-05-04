# -*- coding: utf-8 -*-

from django.conf import settings
from django.template import TemplateDoesNotExist
from template_preprocessor.core import compile
from template_preprocessor.core.lexer import CompileException
from template_preprocessor.management.commands.compile_templates import Command as CompileCommand
import codecs
import os
import template_preprocessor.utils
from template_preprocessor.utils import load_template_source
from template_preprocessor.utils import get_options_for_path

def _get_path_form_app(app):
	m = __import__(app)
	if '.' in app:
		parts = app.split('.')
		for p in parts[1:]:
			m = getattr(m, p)
	return m.__path__[0]


def get_template_path(template):
	input = get_template_path.context['input']
	input_dirname = os.path.dirname(input)
	input_dirname_split = os.path.normpath(input_dirname).split(os.path.sep)

	for dir in settings.TEMPLATE_DIRS:
		try:
			dir = os.path.normpath(dir).split(os.path.sep)
			if dir != input_dirname_split[0:len(dir)]:
				continue
			from_template_root = input_dirname_split[len(dir):]
			from_template_basedir = input_dirname_split[:len(dir)]
			from_template_basedir[0] = '/'
			for (template_device, template_skins) in settings.TEMPLATES:
				for skin in reversed(template_skins):
					if from_template_root[:2] == [template_device, skin]:
						pathname = os.path.join(*tuple(from_template_basedir + [template_device, skin, template]))
						if os.path.exists(pathname):
							return pathname
		except IndexError:
			pass

	for dir in settings.TEMPLATE_DIRS:
		p = os.path.join(dir, template)
		if os.path.exists(p):
			return p

	for app in settings.INSTALLED_APPS:
		p = os.path.join(_get_path_form_app(app), 'templates', template)
		if os.path.exists(p):
			return p

	raise TemplateDoesNotExist, template

template_preprocessor.utils.get_template_path = get_template_path
template_preprocessor.utils.get_template_path.context = {'input': None}


class Command(CompileCommand):
	def _compile_template(self, lang, template, input_path, output_path, no_html = False, retry = False):
		if not retry:
			template_preprocessor.utils.get_template_path.context = {'input': input_path}
		try:
			# Create output directory
			self._create_dir(os.path.split(output_path)[0])

			try:
				# Open input file
				code = codecs.open(input_path, 'r', 'utf-8').read()
			except UnicodeDecodeError, e:
				raise CompileException(0, 0, input_path, str(e))
			except IOError, e:
				raise CompileException(0, 0, input_path, str(e))

			# Compile
			if no_html:
				output, context = compile(code, path = input_path, loader = load_template_source, options = get_options_for_path(input_path) + ['no-html'], context_class = self.NiceContext)
			else:
				output, context = compile(code, path = input_path, loader = load_template_source, options = get_options_for_path(input_path), context_class = self.NiceContext)

			# store dependencies
			self._save_template_dependencies(lang, template, context.template_dependencies)
			self._save_first_level_template_dependencies(lang, template, context.include_dependencies, context.extends_dependencies)

			# Open output file
			codecs.open(output_path, 'w', 'utf-8').write(output)

			# Delete -c-recompile file (mark for recompilation) if one such exist.
			if os.path.exists(output_path + '-c-recompile'):
				os.remove(output_path + '-c-recompile')

			return True

		except CompileException, e:
			search_subdirs = True
			if not retry:
				input_path_add = []
				for (template_device, template_skins) in settings.TEMPLATES:
					for skin in reversed(template_skins):
						input_path_add.append([template_device, skin])
						if template.split(os.path.sep)[:2] == [template_device, skin]:
							search_subdirs = False
				success = False
				if search_subdirs:
					root_input_path = input_path[0:-(len(template))]
					root_output_path = output_path[0:-(len(template))]
					for path_add in input_path_add:
						fake_input_path = os.path.join(root_input_path, path_add[0], path_add[1], template)
						new_output_path = os.path.join(root_output_path, path_add[0], path_add[1], template)
						template_preprocessor.utils.get_template_path.context = {'input': fake_input_path}
						if self._compile_template(lang, template, input_path, new_output_path, no_html = no_html, retry = True):
							success = True
				if success:
					if os.path.exists(output_path + '-c-recompile'):
						os.remove(output_path + '-c-recompile')
					return

			# Try again without html
			if not no_html:
				# Print the error
				self.print_error(u'ERROR:  %s' % unicode(e))

				print u'Trying again with option "no-html"... ',
				if self._compile_template(lang, template, input_path, output_path, no_html = True, retry = retry):
					print 'Succeeded'
				else:
					print 'Failed again'

				# Create recompile mark
				open(output_path + '-c-recompile', 'w').close()

		except TemplateDoesNotExist, e:
			if self.verbosity >= 2:
				print u'WARNING: Template does not exist:  %s' % unicode(e)
