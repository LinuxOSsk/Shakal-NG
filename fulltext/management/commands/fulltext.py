# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from fulltext import registry as fulltext_registry


class Command(BaseCommand):
	help = "Fulltext management"
	__progress = False

	def __prog(self, iterable, **kwargs):
		if self.__progress:
			from tqdm import tqdm
			return tqdm(iterable, **kwargs)
		else:
			return iterable

	def add_arguments(self, parser):
		parser.add_argument('--progress', action='store_true')
		subparsers = parser.add_subparsers(description="Subcommand", required=True)
		subparsers.dest = 'subcommand'
		subparsers.add_parser("update")

	def handle(self, *args, **options):
		subcommand = options.pop('subcommand')
		self.__progress = options.pop('progress')
		return getattr(self, subcommand)(**options)

	def update(self, **options): # pylint: disable=unused-argument
		for index in fulltext_registry:
			self.update_index(index())

	def update_index(self, index):
		bulk_items = []
		for obj in self.__prog(index.get_index_queryset(), desc=index.get_model().__name__):
			instance = index.get_index(obj)
			print(f'created: {instance.created}')
			print(f'updated: {instance.updated}')
			print(f'author: {instance.author}')
			print(f'authors_name: {instance.authors_name}')
			print(f'title: {instance.title}')
			print(f'document:\n{instance.document}')
			print(f'comments:\n{instance.comments}\n')
			bulk_items.append(instance)
		print(bulk_items)
