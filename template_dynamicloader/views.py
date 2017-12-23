# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from copy import deepcopy

from django.http import HttpResponseRedirect, QueryDict
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from .forms import ChangeTemplateHiddenForm
from .utils import switch_template


@require_POST
def change(request):
	form = ChangeTemplateHiddenForm(request.POST)
	response = HttpResponseRedirect(request.POST.get('next', reverse('home')))
	if form.is_valid() and 'change_style' in request.POST:
		switch_template(response, **form.cleaned_data)
	return response


class TemplateListView(TemplateView):
	template_name = 'template_dynamicloader/template_list.html'
	available_templates = [
		{
			'name': 'alpha',
			'verbose_name': 'Alpha',
			'variants': [
				{
					'settings': {'font-size': 13},
					'verbose_name': 'Drobný text'
				}
			]
		},
		{
			'name': 'default',
			'verbose_name': 'Starý štýl',
		},
		{
			'name': '386',
			'verbose_name': '386',
		},
	]

	def get_context_data(self, **kwargs):
		available_templates = []
		base_url = reverse('home')
		for template in self.available_templates:
			template = deepcopy(template)
			query = QueryDict('', mutable=True)
			query['switch_template'] = template['name']
			template['url'] = base_url + '?' + query.urlencode()
			for variant in template.get('variants', []):
				query = QueryDict('', mutable=True)
				query['switch_template'] = template['name'] + '::' + json.dumps(variant.get('settings', {}))
				variant['url'] = base_url + '?' + query.urlencode()
			available_templates.append(template)
		return super(TemplateListView, self).get_context_data(
			available_templates=available_templates,
			**kwargs
		)
