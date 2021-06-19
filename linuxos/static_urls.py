# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, RedirectView
from django.urls import path


sites = (
	('co_je_linux', 'co-je-linux'),
	('internet', 'internet'),
	('kancelaria', 'kancelaria'),
	('multimedia', 'multimedia'),
	('hry', 'hry'),
	('veda', 'veda'),
	('odkazy', 'odkazy'),

	('portal_podporte_nas', 'portal-podporte-nas'),
	('portal_vyvoj', 'portal-vyvoj'),
	('export', 'export'),
	('team', 'team'),

	('netscreens', 'internet/screenshoty'),
	('officescreens', 'kancelaria/screenshoty'),
	('mmscreens', 'multimedia/screenshoty'),
	('vedascreens', 'veda/screenshoty'),

	('ochrana_osobnych_udajov', 'ochrana-osobnych-udajov'),
)

sites_urls = [path(u[1] + '/', TemplateView.as_view(template_name='static/' + u[1] + '.html'), name="page_" + u[1]) for u in sites]
redirect_urls = [path(u[0] + '/index.html', RedirectView.as_view(url='/' + u[1] + '/', permanent=True)) for u in sites]

urlpatterns = sites_urls + redirect_urls
