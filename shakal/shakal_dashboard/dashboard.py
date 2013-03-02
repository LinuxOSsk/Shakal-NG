# -*- coding: utf-8 -*-

from admin_tools.dashboard import Dashboard
from admin_tools.dashboard.modules import RecentActions
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import modules

class ShakalIndexDashboard(Dashboard):
	columns = 2

	class Media:
		css = ('admin/shakal_dashboard/dashboard.css', )

	def init_with_context(self, context):
		appgroups = self.get_application_groups()
		for title, kwargs in appgroups:
			GroupClass = self.import_module_class(kwargs.pop('module'))
			self.children.append(GroupClass(title, **kwargs))
		self.children.append(RecentActions(_('Recent Actions'), 5, enabled=False, collapsible=False))

	def get_application_groups(self):
		groups = []
		known_apps = []
		for title, group in getattr(settings, 'SHAKAL_DASHBOARD_APP_GROUPS', ()):
			if '*' in group['models']:
				default_module = 'AppList'
				module_kwargs = {'exclude': known_apps + list(group.get('exclude', []))}
			else:
				default_module = 'AppIconList'
				module_kwargs = {
					'models': group['models'],
					'exclude': group.get('exclude', ()),
				}
				known_apps.extend(group['models'])
			module_kwargs['module'] = group.get('module', default_module)
			module_kwargs['collapsible'] = group.get('collapsible', False)
			groups.append((title, module_kwargs))
		return groups

	def import_module_class(self, module_class):
		return getattr(modules, module_class)
