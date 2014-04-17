# -*- coding: utf-8 -*-
from django.contrib.admin.templatetags.admin_modify import register


@register.inclusion_tag('admin/submit_line.html', takes_context=True)
def submit_row(context):
	opts = context['opts']
	change = context['change']
	is_popup = context['is_popup']
	save_as = context['save_as']
	ctx = {
		'opts': opts,
		'show_delete_link': (not is_popup and context['has_delete_permission'] and change and context.get('show_delete', True)),
		'show_save_as_new': not is_popup and change and save_as,
		'show_save_and_add_another': context['has_add_permission'] and not is_popup and (not save_as or context['add']),
		'show_save_and_continue': not is_popup and context['has_change_permission'],
		'is_popup': is_popup,
		'show_save': True,
		'preserved_filters': context.get('preserved_filters'),
	}
	if context.get('original') is not None:
		ctx['original'] = context['original']
	if context.get('changelist_actions') is not None:
		ctx['changelist_actions'] = context['changelist_actions']
	return ctx
