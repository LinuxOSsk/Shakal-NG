# -*- coding: utf-8 -*-
#pylint: disable=W0611,F0401
from django.forms.widgets import Textarea
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.safestring import mark_safe


try:
	from suit.widgets import SuitDateWidget as DateInput, SuitTimeWidget as TimeInput, SuitSplitDateTimeWidget as DateTimeInput, EnclosedInput, AutosizedTextarea
except ImportError:
	from django.forms import DateInput, TimeInput, DateTimeInput, TextInput, Textarea as AutosizedTextarea
	class EnclosedInput(TextInput):
		def __init__(self, prepend=None, append=None, *args, **kwargs):
			self.prepend = prepend
			self.append = append
			super(EnclosedInput, self).__init__(*args, **kwargs)


class RichEditorWidget(Textarea):
	class Media:
		js = [
			'js/lib.js',
			'js/richeditor/editor.js',
		]
		css = {
			'all': ('js/wymeditor/skins/suit/skin.css', )
		}

	def __init__(self, attrs=None, **kwargs):
		attrs = attrs or {}
		attrs.update({'class': 'wymeditor input-xlarge'})
		super(RichEditorWidget, self).__init__(attrs, **kwargs)

	def render(self, name, value, attrs=None, **kwargs):
		supported_tags = self.attrs.pop('supported_tags', {})
		widget = super(RichEditorWidget, self).render(name, value, attrs, **kwargs)
		self.attrs['supported_tags'] = supported_tags

		context = {
			'name': name,
			'lang': translation.get_language(),
			'widget': widget,
			'force_editor': 'wymeditor',
			'skin': 'compact',
		}
		return mark_safe(render_to_string('widgets/editor.html', context))
