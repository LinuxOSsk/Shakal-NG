# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from template_dynamicloader.utils import get_template_settings


def style(request):
	template_skin, template_css, template_settings = get_template_settings(request)
	return {
		'current_style': template_skin,
		'style_options': template_settings,
		'style_css': template_css
	}
