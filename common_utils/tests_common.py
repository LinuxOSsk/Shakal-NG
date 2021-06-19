# -*- coding: utf-8 -*-
import os
import unittest
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models.fields.files import FieldFile
from django.forms import BaseForm
from django.shortcuts import resolve_url
from django.test import LiveServerTestCase
from django.urls import reverse


User = get_user_model()


class LoggedUserTestMixin(object):
	def login(self, username, password, is_superuser=False, is_staff=False):
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			user = User(username=username)
			user.set_password(password)
			user.is_staff = is_staff
			user.is_superuser = is_superuser
			user.save()
		logged = self.client.login(username=username, password=password)
		if logged:
			return user
		else:
			return None


class ProcessFormTestMixin(object):
	def get_url(self, url, *args, **kwargs):
		return self.client.get(resolve_url(url, *args, **kwargs))

	def extract_form(self, url, form_context_name='form'):
		response = self.get_url(url)
		return response.context_data[form_context_name]

	def extract_form_data(self, form):
		data = dict()
		for field in form.fields:
			fieldname = ((form.prefix + '-') if form.prefix else '') + field
			if field == 'id' and not fieldname in data and form.instance:
				data[fieldname] = form.instance.pk
			if not fieldname in data:
				data[fieldname] = ''
			if field in form.initial:
				data[fieldname] = form.initial.get(field)
			if field in form.data:
				data[fieldname] = form.data.get(field)
			if fieldname in data and data[fieldname] is None:
				data[fieldname] = ''
			if isinstance(data[fieldname], FieldFile):
				data[fieldname] = ''
			if isinstance(data[fieldname], datetime):
				dt = data[fieldname]
				del data[fieldname]
				data[fieldname + '_0'] = dt.strftime("%Y-%m-%d")
				data[fieldname + '_1'] = dt.strftime("%H:%M:%S")
		return data

	def fill_form(self, form, fill_data):
		if isinstance(form, BaseForm):
			data = self.extract_form_data(form)
		else:
			data = form.copy()

		for key in fill_data:
			self.assertTrue(key in data)
			data[key] = fill_data[key]
		return data

	def send_form_data(self, url, data, **kwargs):
		return self.client.post(resolve_url(url), data, **kwargs)


class AdminSiteTestCase(LoggedUserTestMixin, ProcessFormTestMixin, LiveServerTestCase):
	def login(self, username, password, is_superuser=True, is_staff=True):
		return super(AdminSiteTestCase, self).login(username, password, is_superuser, is_staff)

	def get_admin_url(self, view, args=None, kwargs=None, app_label=None, model=None): #pylint: disable=too-many-arguments
		if app_label is None:
			app_label = self.__module__.rpartition('.')[0]
		if model is None:
			model = getattr(self, "model")
		args = args or []
		kwargs = kwargs or []
		return reverse("admin:%s_%s_%s" % (app_label, model, view), args=args, kwargs=kwargs)

	def get_admin_view_response(self, view, args=None, kwargs=None, post=None):
		url = self.get_admin_url(view, args=args or [], kwargs=kwargs or {})
		if post:
			response = self.client.post(url, data=post)
		else:
			response = self.client.get(url)
		return response

	def get_response_form_data(self, response):
		form_data = self.extract_form_data(response.context_data['adminform'].form)
		for formset in response.context_data['inline_admin_formsets']:
			form_data.update(self.extract_form_data(formset.formset.management_form))
			for form in formset.formset.forms:
				form_data.update(self.extract_form_data(form))
		return form_data

	def check_form_save_view(self, view, data, check_redirect, args=None):
		response = self.get_admin_view_response(view, args=args or [])
		self.assertEqual(response.status_code, 200)
		form_data = self.get_response_form_data(response)
		form_data.update(data)
		form_data['_continue'] = ''
		response = self.get_admin_view_response(view, post=form_data, args=args or [])
		if check_redirect:
			if response.status_code == 200:
				print(response.context_data['adminform'].form.errors)
			self.assertEqual(response.status_code, 302)

		ret = {}
		if response.status_code == 302:
			response = self.client.get(response.url)
			ret['instance'] = response.context_data['adminform'].form.instance

		ret['response'] = response
		return ret

	def check_add(self, data, check_redirect=True):
		return self.check_form_save_view("add", data, check_redirect)

	def check_change(self, object_pk, data, check_redirect=True):
		return self.check_form_save_view("change", data, check_redirect, args=[object_pk])

	def check_action(self, object_pk, action, data, check_redirect=True):
		if action is not None:
			data = data.copy()
			data['_' + action] = ''
		return self.check_form_save_view("change", data, check_redirect, args=[object_pk])

	def check_delete(self, object_pk, check_redirect=True):
		response = self.get_admin_view_response("delete", args=[object_pk])
		self.assertEqual(response.status_code, 200)
		response = self.get_admin_view_response("delete", args=[object_pk], post={'post': 'yes'})
		if check_redirect:
			self.assertEqual(response.status_code, 302)

		ret = {}
		ret['response'] = response
		return ret

	def check_changelist(self):
		response = self.get_admin_view_response("changelist")
		self.assertEqual(response.status_code, 200)
		return {'response': response}


def fts_test(cls):
	if 'SKIP_FTS_TESTS' in os.environ:
		return unittest.skip(cls)
	return cls


class FrontendTest(ProcessFormTestMixin, LiveServerTestCase):
	def check_url(self, url, *args, **kwargs):
		response = self.get_url(url, *args, **kwargs)
		self.assertEqual(response.status_code, 200)
		return response


def create_image(size=None, color=None, filetype='png', basename='image'):
	from PIL import Image
	from io import BytesIO

	size = size or (50, 50)
	color = color or (256, 0, 0)

	file_obj = BytesIO()

	im = Image.new('RGBA' if filetype == 'png' else 'RGB', size=size, color=color)
	im.save(file_obj, filetype)

	file_obj.name = basename + '.' + filetype
	file_obj.seek(0)
	return file_obj
