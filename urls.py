from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from article.views import ArticleDetailView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Examples:
	# url(r'^shakal/', include('shakal.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	url(r'^$', 'shakal.views.home', name='home'),
	url(r'^admin/', include(admin.site.urls), name='admin'),
	url(r'^article/(?P<slug>\S+)/$', ArticleDetailView.as_view(), name='article_detail'),
	url(r'^article-category/(?P<slug>\S+)/(?P<page>\d+)/$', 'article.views.view_category', name='article_category_page'),
	url(r'^article-category/(?P<slug>\S+)/$', 'article.views.view_category', {'page': '1'}, name='article_category'),
	url(r'^comments/', include('threaded_comments.urls')),
)
