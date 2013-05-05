from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.contenttypes import views as contenttype_views
from django.utils.translation import ugettext_lazy as _
from views import home
from accounts import urls as accounts_urls
from article import urls as article_urls
from threaded_comments import urls as comments_urls
from forum import urls as forum_urls
from news import urls as news_urls
from notifications import urls as notifications_urls
from maintenance import urls as maintenance_urls
from search.views import SearchView
from polls import urls as polls_urls
from wiki import urls as wiki_urls

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', home, name = 'home'),
	url(r'^', include('linuxos.urls')),
	url(_(r'^admin/'), include(admin.site.urls)),
	url(_(r'^accounts/'), include(accounts_urls.urlpatterns)),
	url(_(r'^article/'), include(article_urls.urlpatterns)),
	url(_(r'^comments/'), include(comments_urls.urlpatterns)),
	url(_(r'^forum/'), include(forum_urls.urlpatterns)),
	url(_(r'^maintenance/'), include(maintenance_urls.urlpatterns)),
	url(_(r'^news/'), include(news_urls.urlpatterns)),
	url(_(r'^notifications/'), include(notifications_urls.urlpatterns)),
	url(_(r'^polls/'), include(polls_urls.urlpatterns)),
	url(_(r'^wiki/'), include(wiki_urls.urlpatterns)),
	url(_(r'^template-change/$'), 'template_dynamicloader.views.change', name = 'template-change'),
	url(_(r'^search/'), SearchView(), name = 'haystack_search'),
	url(r'^v/(?P<content_type_id>\d+)/(?P<object_id>.+)/$', contenttype_views.shortcut, name = 'view-object'),
	url(r'^admin_tools/', include('admin_tools.urls')),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
	)
else:
	handler500 = 'shakal.views.error_500'
