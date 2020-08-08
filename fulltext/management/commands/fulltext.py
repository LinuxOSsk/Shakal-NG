# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from ...utils import update_search_index
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
			update_search_index(index(), progress=self.__prog)
