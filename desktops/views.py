# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from braces.views import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.views.generic import DetailView, CreateView, UpdateView

from .forms import DesktopCreateForm, DesktopUpdateForm
from .models import Desktop
from common_utils.generic import ListView


class DesktopList(ListView):
	queryset = Desktop.objects.all()
	category_key = 'author'
	category_field = 'author_id'
	category_context = 'author'
	category_model = get_user_model()
	paginate_by = 20

	def get_queryset(self):
		return super(DesktopList, self).get_queryset().select_related('author')


class DesktopCreate(LoginRequiredMixin, CreateView):
	model = Desktop
	form_class = DesktopCreateForm

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super(DesktopCreate, self).form_valid(form)


class DesktopUpdate(LoginRequiredMixin, UpdateView):
	form_class = DesktopUpdateForm

	def get_queryset(self):
		return (super(DesktopUpdate, self).get_queryset()
			.filter(author=self.request.user))


class DesktopDetail(DetailView):
	queryset = Desktop.objects.all()

	def get_context_data(self, **kwargs):
		next_desktops = (Desktop.objects
			.filter(author=self.object.author, pk__lt=self.object.pk)[:3])
		other_desktops = (
			('Ďalšie desktopy', next_desktops),
		)
		return (super(DesktopDetail, self)
			.get_context_data(other_desktops=other_desktops, **kwargs))
