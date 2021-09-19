# -*- coding: utf-8 -*-
from suit.apps import DjangoSuitConfig, SUIT_FORM_SIZE_XX_LARGE, SUIT_FORM_SIZE_XXX_LARGE, SUIT_FORM_SIZE_FULL
from suit.menu import ParentItem, ChildItem


class SuitConfig(DjangoSuitConfig):
	layout = 'vertical'
	verbose_name = 'Shakal CMS'
	list_per_page = 50
	menu = [
		ParentItem(
			label='Ankety',
			icon='fa fa-tasks',
			permissions='polls.change_poll',
			children=[
				ChildItem(model='polls.poll'),
			],
		),
		ParentItem(
			label='Blogy',
			icon='fa fa-pencil',
			permissions='blog.change_post',
			children=[
				ChildItem(model='blog.post'),
				ChildItem(model='blog.blog'),
				ChildItem(model='blog.postcategory'),
				ChildItem(model='blog.postseries'),
			],
		),
		ParentItem(
			label='Články',
			icon='fa fa-font',
			permissions='article.change_article',
			children=[
				ChildItem(model='article.article'),
				ChildItem(model='article.category'),
				ChildItem(model='article.series'),
			],
		),
		ParentItem(
			label='Desktopy',
			icon='fa fa-image',
			permissions='desktops.change_desktop',
			children=[
				ChildItem(model='desktops.desktop'),
			],
		),
		ParentItem(
			label='E-maily',
			icon='fa fa-envelope',
			permissions='django_email_log.change_email',
			children=[
				ChildItem(model='django_email_log.email'),
			],
		),
		ParentItem(
			label='Fórum',
			icon='fa fa-list',
			permissions='forum.change_topic',
			children=[
				ChildItem(model='forum.topic'),
				ChildItem(model='forum.section'),
			],
		),
		ParentItem(
			label='Komentre',
			icon='fa fa-comments',
			permissions='comments.change_rootheader',
			children=[
				ChildItem(model='comments.rootheader'),
				ChildItem(model='comments.comment'),
			],
		),
		ParentItem(
			label='Používatelia',
			icon='fa fa-user',
			permissions='accounts.change_user',
			children=[
				ChildItem(model='accounts.user'),
				ChildItem(model='auth.group'),
			],
		),
		ParentItem(
			label='Správy',
			icon='fa fa-globe',
			permissions='news.change_news',
			children=[
				ChildItem(model='news.news'),
				ChildItem(model='news.category'),
			],
		),
		ParentItem(
			label='Poznámky',
			icon='fa fa-sticky-note',
			permissions='notes.note',
			children=[
				ChildItem(model='notes.note'),
			],
		),
		ParentItem(
			label='Tweety',
			icon='fa fa-twitter',
			permissions='tweets.tweet',
			children=[
				ChildItem(model='tweets.tweet'),
			],
		),
		ParentItem(
			label='Wiki',
			icon='fa fa-wikipedia-w',
			permissions='wiki.change_page',
			children=[
				ChildItem(model='wiki.page'),
			],
		),
	]
	form_size = {
		'default': SUIT_FORM_SIZE_XX_LARGE,
		'widgets': {
			'RelatedFieldWidgetWrapper': SUIT_FORM_SIZE_XXX_LARGE,
			'RichEditorWidget': SUIT_FORM_SIZE_FULL,
			'GeopositionWidget': SUIT_FORM_SIZE_FULL,
		}
	}
