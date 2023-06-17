# -*- coding: utf-8 -*-
from django.core.management import CommandParser, BaseCommand


def add_subparsers(cmd: BaseCommand, parser: CommandParser, **kwargs) -> CommandParser:
	class SubParser(CommandParser):
		def __init__(self, **kwargs):
			kwargs['called_from_command_line'] = getattr(cmd, "_called_from_command_line", None)
			super().__init__(**kwargs)
	return parser.add_subparsers(parser_class=SubParser, **kwargs)
