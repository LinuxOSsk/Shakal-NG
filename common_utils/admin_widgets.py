# -*- coding: utf-8 -*-
# pylint: disable=unused-import
from __future__ import unicode_literals

from rich_editor.widgets import RichOriginalEditor


try:
	from suit.widgets import SuitDateWidget as DateInput, SuitTimeWidget as TimeInput, SuitSplitDateTimeWidget as DateTimeInput, EnclosedInput, AutosizedTextarea
except ImportError:
	from django.forms import DateInput, TimeInput, DateTimeInput, TextInput, Textarea as AutosizedTextarea
	class EnclosedInput(TextInput):
		def __init__(self, prepend=None, append=None, *args, **kwargs):
			self.prepend = prepend
			self.append = append
			super(EnclosedInput, self).__init__(*args, **kwargs) #pylint: disable=bad-super-call


class RichEditorWidget(RichOriginalEditor):
	template_name = 'widgets/admin_richeditor.html'

	class Media:
		js = [
			'js/richeditor/editor.js',
		]
		css = {
			'screen': ['css/editor.light.css'],
		}

	def __init__(self, *args, **kwargs):
		super(RichEditorWidget, self).__init__(*args, **kwargs)
		self.formats = (('raw', 'Nefiltrovaný text'), ) + self.formats
		self.skin = 'compact'
