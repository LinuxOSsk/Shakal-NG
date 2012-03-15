# -*- coding: utf-8 -*-

backgrounds = {
	'layout': 'vertical',
	'output': 'templates/static/desktop/default/images/backgrounds.png',
	'images': [
		{
			'name': 'logo',
			'src': 'templates/static/desktop/default/images/export/logo.png',
			'mode': 'no-repeat', 'width': 240, 'height': 80
		},
		{
			'name': 'breadcrumb_left_bg',
			'src': 'templates/static/desktop/default/images/export/breadcrumb_left_bg.png',
			'mode': 'no-repeat', 'width': 8, 'height': 36
		},
		{
			'name': 'breadcrumb_passive',
			'src': 'templates/static/desktop/default/images/export/breadcrumb_passive.png',
			'mode': 'no-repeat', 'width': 320, 'height': 31
		},
		{
			'name': 'breadcrumb_active',
			'src': 'templates/static/desktop/default/images/export/breadcrumb_active.png',
			'mode': 'no-repeat', 'width': 320, 'height': 31
		},
		{
			'name': 'breadcrumb_bg',
			'src': 'templates/static/desktop/default/images/export/breadcrumb_bg.png',
			'mode': 'repeat-x', 'width': 8, 'height': 36
		},
	]
}

IMAGES = {
	'backgrounds': backgrounds
}
