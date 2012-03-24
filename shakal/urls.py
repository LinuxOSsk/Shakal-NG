from django.conf.urls import patterns, include, url
from django.contrib import admin
from shakal.article.views import ArticleDetailView

admin.autodiscover()

urlpatterns = patterns('',
	 url(r'^$', 'shakal.views.home', name='home'),
	 url(r'^admin/', include(admin.site.urls), name='admin'),
	 url(r'^article/(?P<slug>\S+)/$', ArticleDetailView.as_view(), name='article_detail'),
	 url(r'^article-category/(?P<slug>\S+)/(?P<page>\d+)/$', 'shakal.article.views.view_category', name='article_category_page'),
	 url(r'^article-category/(?P<slug>\S+)/$', 'shakal.article.views.view_category', {'page': '1'}, name='article_category'),
	 url(r'^comments/', include('shakal.threaded_comments.urls')),
)
