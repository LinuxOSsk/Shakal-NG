from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from views import home
from accounts import urls as accounts_urls
from article import urls as article_urls

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', home, name = 'home'),
	url(_(r'^admin/'), include(admin.site.urls)),
	url(_(r'^accounts/'), include(accounts_urls.urlpatterns)),
	url(_(r'^article/'), include(article_urls.urlpatterns)),
)
