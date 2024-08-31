from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.functional import cached_property
from pathlib import Path

from web.sitemaps import sitemaps


class Command(BaseCommand):
	command = None
	help = 'Generates sitemaps files to a predefined directory.'

	@cached_property
	def root_dir(self):
		return Path(settings.STATIC_ROOT)

	def normalize_url(self, url):
		if url[-1] != '/':
			url += '/'
		if not url.startswith(('http://', 'https://')):
			url = settings.BASE_URI + url
		return url

	def handle(self, *args, **options):
		print(sitemaps)
