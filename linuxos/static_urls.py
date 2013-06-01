# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView


sites = (
	('co_je_linux', 'co-je-linux'),
	('internet', 'internet'),
	('kancelaria', 'kancelaria'),
	('multimedia', 'multimedia'),
	('hry', 'hry'),
	('veda', 'veda'),
	('odkazy', 'odkazy'),

	('reklama', 'reklama'),
	('portal_podporte_nas', 'portal-podporte-nas'),
	('export', 'export'),
	('team', 'team'),

	('netscreens', 'internet/screenshoty'),
	('officescreens', 'kancelaria/screenshoty'),
)

sites_urls = map(lambda u: url('^' + u[1] + '/$', TemplateView.as_view(template_name = 'static/' + u[1] + '.html'), name = "page_" + u[1]), sites)
redirect_urls = map(lambda u: url('^' + u[0] + '/index.html$', RedirectView.as_view(url = '/' + u[1] + '/')), sites)

urlpatterns = patterns('', *(sites_urls + redirect_urls))
