# -*- coding: utf-8 -*-
from django import forms
from models import Topic

class TopicForm(forms.ModelForm):
	class Meta:
		model = Topic
		exclude = ('user', 'time', )
		fields = ('section', 'username', 'subject', 'text', )

class TopicLoggedForm(TopicForm):
	class Meta:
		model = Topic
		exclude = ('username', 'user', 'time', )
		fields = ('section', 'subject', 'text', )
