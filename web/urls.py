from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.contenttypes import views as contenttype_views
from django.utils.translation import ugettext_lazy as _

from search.views import SearchView


urlpatterns = patterns('',
	url(r'^$', 'web.views.Home', name='home'),
	url(r'^', include('linuxos.urls')),
	url(_(r'^login/'), include('allauth.urls')),
	url(_(r'^accounts/'), include('accounts.urls', namespace='accounts')),
	url(_(r'^article/'), include('article.urls', namespace='article')),
	url(_(r'^blog/'), include('blog.urls', namespace='blog')),
	url(_(r'^comments/'), include('comments.urls', namespace='comments')),
	url(r'^desktopy/', include('desktops.urls', namespace='desktops')),
	url(_(r'^forum/'), include('forum.urls', namespace='forum')),
	#url(_(r'^maintenance/'), include('maintenance.urls', namespace='maintenance')),
	url(_(r'^news/'), include('news.urls', namespace='news')),
	url(_(r'^notifications/'), include('notifications.urls', namespace='notifications')),
	url(_(r'^polls/'), include('polls.urls', namespace='polls')),
	url(_(r'^wiki/'), include('wiki.urls', namespace='wiki')),
	url(_(r'^template-change/$'), 'template_dynamicloader.views.change', name='template-change'),
	url(_(r'^search/'), SearchView(), name='haystack_search'),
	url(r'^v/(?P<content_type_id>\d+)/(?P<object_id>.+)/$', contenttype_views.shortcut, name='view-object'),
	url(_(r'^admin/'), include(admin.site.urls)),
	url(_(r'^admin_dashboard/'), include('admin_dashboard.urls', namespace='admin_dashboard')),
	url(r'^api/editor/', include('rich_editor.urls', namespace='rich_editor')),
	url(r'^hijack/', include('hijack.urls')),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
	)
else:
	handler404 = 'web.views.error_404'
	handler500 = 'web.views.error_500'
