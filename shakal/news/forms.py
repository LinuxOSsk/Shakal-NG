# -*- coding: utf-8 -*-

from django import forms
from models import News

class NewsForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		logged = kwargs.pop('logged', False)
		super(NewsForm, self).__init__(*args, **kwargs)
		if logged:
			del(self.fields['authors_name'])

	class Meta:
		model = News
		exclude = ('author', 'time', 'approved', )
		fields = ('subject', 'authors_name', 'subject', 'short_text', 'long_text', )
