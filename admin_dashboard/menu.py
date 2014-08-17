# -*- coding: utf-8 -*-
import re

from admin_tools.menu import items, Menu
from admin_tools.utils import get_admin_site_name
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, resolve, NoReverseMatch
from django.template.defaultfilters import capfirst
from django.utils.translation import ugettext_lazy as _

from appgroups import get_application_groups
from common_utils import get_meta


RE_CHANGE_URL = re.compile("(.+)_([^_]+)_change")


class ModelList(items.ModelList):
	def init_with_context(self, context):
		listitems = self._visible_models(context['request'])
		for model, perms in listitems:
			if perms['change']:
				self.children.append(items.MenuItem(title = capfirst(get_meta(model).verbose_name_plural), url = self._get_admin_change_url(model, context)))


class ReturnToSiteItem(items.MenuItem):
	title = _('Return to site')
	url = '/'
	css_classes = ['returntosite']

	def init_with_context(self, context):
		super(ReturnToSiteItem, self).init_with_context(context)
		edited_model = self.get_edited_object(context['request'])
		if edited_model:
			try:
				self.url = edited_model.get_absolute_url()
			except (AttributeError, NoReverseMatch):
				pass

	def get_edited_object(self, request):
		resolved = resolve(request.path_info)
		if resolved.namespace == 'admin' and resolved.url_name.endswith('_change'):
			match = RE_CHANGE_URL.match(resolved.url_name)
			if not match:
				return None
			object_id = int(resolved.args[0])
			return self.get_object_for_model(match.group(1), match.group(2), object_id)
		return None

	def get_object_for_model(self, app_label, model_name, object_id):
		try:
			object_type = ContentType.objects.get_by_natural_key(app_label, model_name)
		except ContentType.DoesNotExist:
			return None

		try:
			return object_type.get_object_for_this_type(pk = object_id)
		except ObjectDoesNotExist:
			return None


class AdminMenu(Menu):
	def init_with_context(self, context):
		site_name = get_admin_site_name(context)
		self.children += [
			items.MenuItem(_('Dashboard'), reverse('{0}:index'.format(site_name))),
			items.Bookmarks(),
		]
		for title, kwargs in get_application_groups():
			self.children.append(ModelList(title, **kwargs))
		self.children.append(ReturnToSiteItem())
