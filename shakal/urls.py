from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from views import home
from accounts import urls as accounts_urls
from article import urls as article_urls
from forum import urls as forum_urls
from news import urls as news_urls

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', home, name = 'home'),
	url(r'^', include('shakal.linuxos.urls')),
	url(_(r'^admin/'), include(admin.site.urls)),
	url(_(r'^accounts/'), include(accounts_urls.urlpatterns)),
	url(_(r'^article/'), include(article_urls.urlpatterns)),
	url(_(r'^forum/'), include(forum_urls.urlpatterns)),
	url(_(r'^news/'), include(news_urls.urlpatterns)),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
	)
