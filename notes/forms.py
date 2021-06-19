# -*- coding: utf-8 -*-
from django import forms

from .models import Note
from common_utils.forms import AuthorsNameFormMixin


class NoteForm(AuthorsNameFormMixin, forms.ModelForm):
	class Meta:
		model = Note
		fields = ('subject', 'original_text', 'is_public')
