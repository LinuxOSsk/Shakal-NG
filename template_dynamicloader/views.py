# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST

from template_dynamicloader.forms import ChangeTemplateHiddenForm
from template_dynamicloader.utils import switch_template


@require_POST
def change(request):
	form = ChangeTemplateHiddenForm(request.POST)
	if form.is_valid() and 'change_style' in request.POST:
		switch_template(request, **form.cleaned_data)
	return HttpResponseRedirect(reverse('home'))
