# -*- coding: utf-8 -*-
from django.urls import path

from . import views


app_name = 'accounts'

urlpatterns = [
	path('', views.UserZone.as_view(), name='user_zone'),
	path('<int:pk>/', views.Profile.as_view(), name='profile'),
	path('<int:pk>/prispevky/', views.UserPosts.as_view(), name='user_posts'),
	path('<int:pk>/prispevky/clanky/<page:page>', views.UserPostsArticle.as_view(), name='user_posts_article'),
	path('<int:pk>/prispevky/blogy/<page:page>', views.UserPostsBlogpost.as_view(), name='user_posts_blogpost'),
	path('<int:pk>/prispevky/spravy/<page:page>', views.UserPostsNews.as_view(), name='user_posts_news'),
	path('<int:pk>/prispevky/forum-temy/<page:page>', views.UserPostsForumTopic.as_view(), name='user_posts_forumtopic'),
	path('<int:pk>/prispevky/komentare/<page:page>', views.UserPostsCommented.as_view(), name='user_posts_commented'),
	path('<int:pk>/prispevky/wiki/<page:page>', views.UserPostsWikiPage.as_view(), name='user_posts_wikipage'),
	path('<int:pk>/mapa/', views.UserMap.as_view(), name='user_map'),
	path('ja/', views.MyProfile.as_view(), name='my_profile'),
	path('ja/sledovane/<page:page>', views.MyWatched.as_view(), name='my_watched'),
	path('ja/navstivene/<page:page>', views.MyViewed.as_view(), name='my_viewed'),
	path('ja/upravit/', views.MyProfileEdit.as_view(), name='my_profile_edit'),
	path('ja/avatar/', views.MyProfileAvatarEdit.as_view(), name='my_profile_avatar_edit'),
	path('ja/pozicia/', views.MyProfilePositionEdit.as_view(), name='my_profile_position_edit'),
	path('mapa-uzivatelov/', views.UsersMap.as_view(), name='users_map'),
]
