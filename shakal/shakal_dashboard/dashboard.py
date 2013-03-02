# -*- coding: utf-8 -*-

from admin_tools.dashboard import Dashboard
from admin_tools.dashboard.modules import RecentActions
from appgroups import get_application_groups
from django.utils.translation import ugettext_lazy as _
import modules

class ShakalIndexDashboard(Dashboard):
	columns = 2

	class Media:
		css = ('admin/shakal_dashboard/dashboard.css', )

	def init_with_context(self, context):
		appgroups = get_application_groups()
		for title, kwargs in appgroups:
			GroupClass = self.import_module_class(kwargs.pop('module'))
			self.children.append(GroupClass(title, **kwargs))
		self.children.append(RecentActions(_('Recent Actions'), 5, enabled=False, collapsible=False))

	def import_module_class(self, module_class):
		return getattr(modules, module_class)
