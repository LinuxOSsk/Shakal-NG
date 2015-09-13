# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max
from django_sample_generator import GeneratorRegister, ModelGenerator, samples

from .models import Comment
from accounts.models import User
from common_utils import get_default_manager
from .utils import update_comments_header


class CommentGenerator(ModelGenerator):
	GENERATE_FOR_MODELS = (
		'article.article',
		'news.news',
	)

	next_id = 0

	subject = samples.SentenceSample()
	user_id = samples.RelationSample(queryset=User.objects.all().order_by("pk"), random_data=True, only_pk=True, fetch_all=True)
	user_name = samples.NameSample()
	original_comment = samples.ParagraphSample()
	submit_date = samples.DateTimeSample()

	def generate_tree(self, parent_id, lft, level):
		if level > 9:
			return []
		comments_flat = []
		comments = [self.get_object() for comment in range(random.randrange(5))]
		for comment in comments:
			comment.id = self.next_id
			comment.lft = lft
			comment.rght = lft + 1
			comment.level = level + 1
			comment.parent_id = parent_id
			lft += 2
			self.next_id += 1
			comments_flat.append(comment)
			if random.randrange(2) == 0:
				child_comments = self.generate_tree(parent_id=comment.id, lft=comment.rght, level=comment.level)
				comments_flat += child_comments
				lft += len(child_comments) * 2
				comment.rght += len(child_comments) * 2
		return comments_flat

	def __iter__(self):
		for model in self.GENERATE_FOR_MODELS:
			model_class = apps.get_model(model)
			ctype = ContentType.objects.get_for_model(model_class)
			for instance in get_default_manager(model_class).all():
				Comment.objects.get_or_create_root_comment(ctype, instance.pk)

		self.next_id = (Comment.objects.aggregate(max_id=Max('id'))['max_id'] or 0) + 1

		for model in self.GENERATE_FOR_MODELS:
			model_class = apps.get_model(model)
			ctype = ContentType.objects.get_for_model(model_class)
			for instance in get_default_manager(model_class).all():
				root_comment = Comment.objects.get_or_create_root_comment(ctype, instance.pk)[0]
				tree = self.generate_tree(parent_id=root_comment.id, lft=root_comment.rght, level=root_comment.level)
				for comment in tree:
					comment.content_type = ctype
					comment.object_id = instance.pk
					comment.filtered_comment = comment.original_comment[1]
					comment.updated = comment.submit_date
					comment.tree_id = root_comment.tree_id
					yield comment
				root_comment.rght = root_comment.rght + len(tree) * 2
				root_comment.save()

	def done(self):
		for model in self.GENERATE_FOR_MODELS:
			model_class = apps.get_model(model)
			ctype = ContentType.objects.get_for_model(model_class)
			for instance in get_default_manager(model_class).all():
				root = Comment.objects.get_or_create_root_comment(ctype, instance.pk)[0]
				update_comments_header(Comment, instance=root)


register = GeneratorRegister()
register.register(CommentGenerator(Comment))
