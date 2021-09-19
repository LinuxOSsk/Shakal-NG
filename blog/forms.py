# -*- coding: utf-8 -*-
from django import forms
from django.db.models import Q, F
from django.forms.models import modelformset_factory
from django.utils.timezone import now

from .models import Blog, Post, PostCategory, PostSeries
from attachment.fields import AttachmentFieldMultiple
from attachment.forms import AttachmentFormMixin
from attachment.models import Attachment


class BlogForm(forms.ModelForm):
	class Meta:
		model = Blog
		fields = ('title', 'original_description', 'original_sidebar',)


class PostForm(forms.ModelForm):
	pub_now = forms.BooleanField(label='Publikovať teraz', required=False)

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request')
		super(PostForm, self).__init__(*args, **kwargs)
		if self.instance and self.instance.published():
			del self.fields['pub_time']
			del self.fields['pub_now']
		else:
			self.fields['pub_time'].required = False
		self.fields['presentation_image'].filter_uploads(self.instance)
		q = Q(blog__isnull=True)
		if hasattr(self.request.user, 'blog'):
			q |= Q(blog_id=self.request.user.blog.id)
		self.fields['category'].queryset = self.fields['category'].queryset.filter(q).order_by(F('blog_id').asc(nulls_last=True), 'pk')
		self.fields['series'].queryset = self.fields['series'].queryset.filter(q).order_by('-updated', 'pk')

	def clean_pub_time(self):
		if 'pub_now' in self.data and self.data['pub_now']:
			return now()
		if not self.cleaned_data['pub_time']:
			raise forms.ValidationError("Nebol zadaný čas publikácie")
		if self.cleaned_data['pub_time'] < now():
			raise forms.ValidationError("Čas publikácie nesmie byť v minulosti")
		return self.cleaned_data['pub_time']

	def save(self, commit=True):
		obj = super().save(commit=False)
		if commit:
			obj.save()
		if obj.series:
			obj.series.updated = obj.updated
			obj.series.save(update_fields=['updated'])
		return obj

	class Meta:
		model = Post
		fields = ('title', 'original_perex', 'original_content', 'pub_time', 'category', 'series', 'presentation_image')


AttachmentFormSetHiddable = modelformset_factory(Attachment, can_delete=True, extra=0, fields=('is_visible',))


class BlogAttachmentForm(AttachmentFormMixin, forms.Form):
	has_visibility = True
	formset = AttachmentFormSetHiddable
	attachment = AttachmentFieldMultiple(label='Príloha', required=False)


class PostCategoryForm(forms.ModelForm):
	class Meta:
		model = PostCategory
		fields = ('title', 'image')


class PostSeriesForm(forms.ModelForm):
	class Meta:
		model = PostSeries
		fields = ('title', 'image')
