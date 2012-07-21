from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import home
from accounts import urls as accounts_urls

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', home, name = 'home'),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/', include(accounts_urls.urlpatterns))
)
