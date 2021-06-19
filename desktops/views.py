# -*- coding: utf-8 -*-
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from django.views.generic import CreateView, UpdateView

from .forms import DesktopCreateForm, DesktopUpdateForm
from .models import Desktop, FavoriteDesktop
from common_utils.generic import ListView, DetailUserProtectedView


class DesktopList(ListView):
	queryset = Desktop.objects.all().order_by('-pk')
	category_key = 'id'
	category_field = 'author'
	category_context = 'author'
	category_model = get_user_model()
	paginate_by = 20

	def get_context_data(self, **kwargs):
		desktops = (Desktop.objects
			.annotated_favorite()
			.filter(created__gte=timezone.now() - timedelta(365))
			.order_by('-favorited_count', '-pk')[:4])
		return super(DesktopList, self).get_context_data(favorite_desktops=desktops, **kwargs)

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
		return (Desktop.objects.all()
			.filter(author=self.request.user))


class DesktopDetail(DetailUserProtectedView):
	queryset = Desktop.objects.annotated_favorite()

	def get_context_data(self, **kwargs):
		next_desktops = (Desktop.objects
			.filter(author=self.object.author, pk__lt=self.object.pk)
			.order_by('-pk')[:3])
		other_desktops = (
			('Ďalšie desktopy', next_desktops),
		)
		favorited = False
		if self.request.user.is_authenticated and self.object.favorited.filter(pk=self.request.user.pk).exists():
			favorited = True
		return (super(DesktopDetail, self)
			.get_context_data(other_desktops=other_desktops, favorited=favorited, **kwargs))

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if request.user.is_authenticated:
			if 'favorite' in request.POST and self.object.author != self.request.user:
				if request.POST['favorite']:
					FavoriteDesktop.objects.get_or_create(desktop=self.object, user=self.request.user)
				else:
					for desk in FavoriteDesktop.objects.all().filter(desktop=self.object, user=self.request.user):
						desk.delete()
		return HttpResponseRedirect(self.object.get_absolute_url())
