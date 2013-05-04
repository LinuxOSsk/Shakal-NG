# -*- coding: utf-8 -*-
from admin_tools.dashboard.modules import AppList
from django.conf import settings


class AppIconList(AppList):
	template = 'admin/dashboard/app_icon_list.html'
	icon_theme_root = settings.STATIC_URL + 'admin/icons/'

	def init_with_context(self, context):
		super(AppIconList, self).init_with_context(context)
		apps = self.children

		for app in apps:
			app_name = app['url'].strip('/').split('/')[-1]
			app['name'] = app_name
			for model in app['models']:
				try:
					model_name = model['change_url'].strip('/').split('/')[-1]
					model['name'] = model_name
					model['icon'] = self.get_icon_for_model(app_name, model_name) or 'default.png'
				except ValueError:
					model['icon'] = 'default.png'

				model['icon'] = self.icon_theme_root + model['icon']
				model['app_name'] = app_name

	def get_icon_for_model(self, app_name, model_name):
		return getattr(settings, 'ADMIN_DASHBOARD_APP_ICONS', {}).get(app_name + '/' + model_name)
