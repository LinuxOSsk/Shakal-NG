# -*- coding: utf-8 -*-
try:
	from suit.widgets import SuitDateWidget as DateInput, SuitTimeWidget as TimeInput, SuitSplitDateTimeWidget as DateTimeInput, EnclosedInput
except ImportError:
	from django.forms import DateInput, TimeInput, DateTimeInput, TextInput
	class EnclosedInput(TextInput):
		def __init__(self, prepend=None, append=None, *args, **kwargs):
			self.prepend = prepend
			self.append = append
			super(EnclosedInput, self).__init__(*args, **kwargs)

try:
	from suit_redactor.widgets import RedactorWidget as RichEditorWidget
except ImportError:
	from django.forms.widgets import Textarea as RichEditorWidget
