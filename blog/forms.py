# -*- coding: utf-8 -*-
from django import forms

from models import Blog
from rich_editor.forms import RichOriginalField


class BlogForm(forms.ModelForm):
	class Meta:
		model = Blog
		fields = ('title', 'pub_date', 'published', )
