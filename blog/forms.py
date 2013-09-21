# -*- coding: utf-8 -*-
from django import forms

from .models import Blog, Post
from rich_editor.forms import RichOriginalField


class BlogForm(forms.ModelForm):
	original_description = RichOriginalField(Blog._meta.get_field('original_description').parsers, label = u'Popis', max_length = 1000, js = True)
	original_sidebar = RichOriginalField(Blog._meta.get_field('original_sidebar').parsers, label = u'Bočný panel', max_length = 1000, js = True)
	class Meta:
		model = Blog
		exclude = ('author', 'slug')


class PostForm(forms.ModelForm):
	original_perex = RichOriginalField(Post._meta.get_field('original_perex').parsers, label = u'Perex', max_length = 1000, js = True)
	original_content = RichOriginalField(Post._meta.get_field('original_content').parsers, label = u'Obsah', max_length = 100000, js = True)
	class Meta:
		model = Post
		exclude = ('blog', 'slug', 'linux', 'pub_time')
