# -*- coding: utf-8 -*-
import random

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max
from django_sample_generator import fields, generator

from .models import Comment
from .utils import update_comments_header
from accounts.models import User
from common_utils import get_default_manager, generator_fields as extra_generator_fields
from common_utils.models import sql_sequence_reset


class CommentGenerator(generator.ModelGenerator):
	GENERATE_FOR_MODELS = (
		'article.article',
		'forum.topic',
		'news.news',
		'blog.post',
		'tweets.tweet',
	)

	next_id = 0
	next_tree_id = 1
	command = None

	subject = extra_generator_fields.SentenceFieldGenerator(max_length=60)
	user_id = fields.ForeignKeyFieldGenerator(
		queryset=User.objects.all().order_by('pk').values_list('pk', flat=True),
		random_data=True
	)
	user_name = extra_generator_fields.NameFieldGenerator()
	original_comment = extra_generator_fields.LongHtmlFieldGenerator(paragraph_count=1)

	class Meta:
		model = Comment
		fields = ('created', 'updated')

	def generate(self, command):
		self.command = command
		ret = super(CommentGenerator, self).generate(command)
		sql_sequence_reset([Comment])
		return ret

	def generate_tree(self, parent_id, lft, level):
		if level > 8:
			return []
		comments_flat = []
		comments = [self.get_object() for comment in range(random.randrange(6))]
		for comment in comments:
			comment.id = self.next_id
			comment.lft = lft
			comment.rght = lft + 1
			comment.level = level + 1
			comment.parent_id = parent_id
			lft += 2
			self.next_id += 1
			comments_flat.append(comment)
			if random.randrange(3) == 0:
				child_comments = self.generate_tree(parent_id=comment.id, lft=comment.rght, level=comment.level)
				comments_flat += child_comments
				lft += len(child_comments) * 2
				comment.rght += len(child_comments) * 2
		if self.command is not None and self.command.verbosity > 1:
			self.command.stdout.write('+', ending='')
		return comments_flat

	def __iter__(self):
		self.next_id = (Comment.objects.all().aggregate(max_id=Max('id'))['max_id'] or 0) + 1

		for model in self.GENERATE_FOR_MODELS:
			model_class = apps.get_model(model)
			ctype = ContentType.objects.get_for_model(model_class)
			for instance in get_default_manager(model_class).all():
				root_comment = Comment(
					parent=None,
					level=0,
					content_type=ctype,
					object_id=instance.pk,
					original_comment='html:',
					filtered_comment='',
					user_name='',
					created=instance.created,
					updated=instance.created,
				)
				root_comment.id = self.next_id
				root_comment.tree_id = self.next_tree_id
				self.next_id += 1
				self.next_tree_id += 1
				tree = self.generate_tree(parent_id=root_comment.id, lft=2, level=root_comment.level) # pylint: disable=no-member
				root_comment.lft = 1
				root_comment.rght = 2 + len(tree) * 2
				yield root_comment
				for comment in tree:
					comment.content_type = ctype
					comment.object_id = instance.pk
					comment.filtered_comment = comment.original_comment
					comment.updated = comment.created
					comment.tree_id = root_comment.tree_id
					yield comment

	def done(self):
		for model in self.GENERATE_FOR_MODELS:
			model_class = apps.get_model(model)
			ctype = ContentType.objects.get_for_model(model_class)
			for instance in get_default_manager(model_class).all():
				root = Comment.objects.get_or_create_root_comment(ctype, instance.pk)[0]
				update_comments_header(Comment, instance=root)
				if self.command is not None and self.command.verbosity > 1:
					self.command.stdout.write('#', ending='')


generators = [
	CommentGenerator(),
]
