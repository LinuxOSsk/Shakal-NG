# -*- coding: utf-8 -*-
from django.apps import AppConfig, apps as global_apps
from django.db import DEFAULT_DB_ALIAS, router
from django.db.models.signals import post_migrate
from django.utils.text import slugify


DEFAULT_CATEGORIES = [
	'Linux',
	'Hardware',
	'Software',
	'Aplikácie',
	'Konfigurácia',
	'Vlastný projekt',
	'Programovanie',
	'Komunita',
	'Humor',
	'Zaujímavosti',
]


def on_migrate(sender, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs): # pylint: disable=unused-argument
	try:
		PostCategory = apps.get_model('blog', 'PostCategory')

		if not router.allow_migrate_model(using, PostCategory) or PostCategory.objects.using(using).exists():
			return

		categories = [
			PostCategory(title=title, slug=slugify(title))
			for title in DEFAULT_CATEGORIES
		]
		PostCategory.objects.bulk_create(categories)
	except LookupError:
		pass


class BlogConfig(AppConfig):
	name = 'blog'
	verbose_name = 'Blog'

	def ready(self):
		post_migrate.connect(on_migrate, sender=self)
