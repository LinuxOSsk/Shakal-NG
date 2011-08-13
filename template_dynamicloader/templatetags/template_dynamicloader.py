from django import template
from django.template.base import Node
register = template.Library()

class TemplateStaticPathNode(Node):
	def __init__(self, path):
		self.path = path

	def render(self, context):
		try:
			return context.get('STATIC_URL', '/') + context['template_dynamic_loader'] + '/' + self.path
		except KeyError:
			return ''


def template_static_path(parser, token):
	bits = token.split_contents()
	if len(bits) != 2:
		raise template.TemplateSyntaxError("Path excepted")
	return TemplateStaticPathNode(bits[1])
register.tag(template_static_path)


class TemplateSetStaticPathNode(Node):
	def __init__(self, path):
		self.path = path

	def render(self, context):
		#context.set('template_dynamicloader_path', path)
		context['template_dynamic_loader'] = self.path;
		return ''


def template_set_static_path(parser, token):
	bits = token.split_contents()
	if len(bits) != 2:
		raise template.TemplateSyntaxError("Path excepted")
	return TemplateSetStaticPathNode(bits[1])
register.tag(template_set_static_path)
