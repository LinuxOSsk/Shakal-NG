# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelChoiceField
from django.forms.widgets import RadioSelect
from models import Topic, Section

class TopicForm(forms.ModelForm):
	section = ModelChoiceField(Section.objects.all(), empty_label=None, widget = RadioSelect())
	def __init__(self, *args, **kwargs):
		super(TopicForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Topic
		exclude = ('user', 'time', )
		fields = ('section', 'username', 'subject', 'text', )

class TopicLoggedForm(TopicForm):
	class Meta:
		model = Topic
		exclude = ('username', 'user', 'time', )
		fields = ('section', 'subject', 'text', )
