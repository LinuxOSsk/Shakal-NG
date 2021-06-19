# -*- coding: utf-8 -*-
# pylint: disable=unused-import
from rich_editor.widgets import RichOriginalEditor


try:
	from suit.widgets import EnclosedInput, AutosizedTextarea
except ImportError:
	from django.forms import TextInput, Textarea as AutosizedTextarea
	class EnclosedInput(TextInput):
		def __init__(self, prepend=None, append=None, *args, **kwargs):
			self.prepend = prepend
			self.append = append
			super().__init__(*args, **kwargs) #pylint: disable=bad-super-call


class RichEditorWidget(RichOriginalEditor):
	class Media:
		js = [
			'js/richeditor/editor2.js',
		]
		css = {
			'screen': ['css/editor.light.css'],
		}

	def get_template_name(self):
		return 'widgets/admin_richeditor.html'

	def __init__(self, *args, **kwargs):
		super(RichEditorWidget, self).__init__(*args, **kwargs)
		self.formats = (('raw', 'Nefiltrovaný text'), ) + self.formats
		self.skin = 'compact'
