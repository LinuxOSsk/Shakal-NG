# -*- coding: utf-8 -*-
from django.conf import settings


def get_application_groups():
	groups = []
	known_apps = []
	for title, group in getattr(settings, 'ADMIN_DASHBOARD_APP_GROUPS', ()):
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
