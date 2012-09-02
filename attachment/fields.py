# -*- coding: utf-8 -*-

from django.forms import FileField
from django.forms.widgets import ClearableFileInput
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

class AttachmentWidget(ClearableFileInput):
	def render(self, name, value, attrs = None):
		max_size = self.attrs.pop('max_size', -1)
		widget = super(AttachmentWidget, self).render(name, value, attrs)
		if max_size >= 0:
			widget += mark_safe("<p class='help upload_size'>"+_("Maximum size is: ")+filesizeformat(max_size)+"</p>")
		self.attrs['max_size'] = max_size
		return widget

class AttachmentField(FileField):
	widget = AttachmentWidget

	def __init__(self, *args, **kwargs):
		super(AttachmentField, self).__init__(**kwargs)
