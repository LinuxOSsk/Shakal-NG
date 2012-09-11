# -*- coding: utf-8 -*-

from django import forms
from antispam.fields import AntispamField
from antispam.forms import AntispamMethodsMixin
from models import News

class NewsForm(forms.ModelForm, AntispamMethodsMixin):
	captcha = AntispamField(required = True)

	def __init__(self, *args, **kwargs):
		logged = kwargs.pop('logged', False)
		request = kwargs.pop('request')
		super(NewsForm, self).__init__(*args, **kwargs)
		if logged:
			del(self.fields['authors_name'])
			del(self.fields['captcha'])
		self.process_antispam(request)

	class Meta:
		model = News
		exclude = ('author', 'time', 'approved', )
		fields = ('subject', 'authors_name', 'subject', 'short_text', 'long_text', )
