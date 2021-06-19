# -*- coding: utf-8 -*-
from template_dynamicloader.utils import get_template_settings


def style(request):
	template = get_template_settings(request)
	return {
		'current_style': template.template,
		'style_options': template.settings,
		'style_css': template.css
	}
