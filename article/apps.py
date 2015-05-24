# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save

from common_utils.cache import delete_tag_factory


class ArticleConfig(AppConfig):
	name = 'article'
	verbose_name = 'Články'

	def ready(self):
		Article = self.get_model('Article')
		delete_article_cache = delete_tag_factory('article.Article')
		post_save.connect(delete_article_cache, sender=Article)
		post_delete.connect(delete_article_cache, sender=Article)
