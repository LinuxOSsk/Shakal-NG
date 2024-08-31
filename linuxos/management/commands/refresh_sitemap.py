import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.functional import cached_property

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
		base_url = self.normalize_url(settings.STATIC_URL)
		sections = []

		for section, site in sitemaps.items():
			pages = site.paginator.num_pages
			for page in range(1, pages + 1):
				filename = f'sitemap-{section}-{page}.xml'
				path = self.root_dir / filename
				last_modification = self.write_section(site, page, path)
				sections.append({
					'location': f'{base_url}{filename}',
					'last_mod': last_modification
				})

		output = render_to_string('sitemap_index.xml', {'sitemaps': sections})
		self.write_file(self.root_dir / 'sitemap.xml', output)

	def write_section(self, site, page, path):
		urls = site.get_urls(page, protocol='https')

		last_mods = [lastmod for lastmod in [u.get('lastmod') for u in urls] if lastmod is not None]
		file_last_mod = max(last_mods) if last_mods else None

		template = getattr(site, 'sitemap_template', 'sitemap.xml')
		output = render_to_string(template, {'urlset': urls})
		self.write_file(path, output)

		return file_last_mod

	def write_file(self, path: Path, content: str):
		tmp_path = path.parent / (path.name + '.suffix')
		with tmp_path.open('w') as f:
			f.write(content)
		os.rename(tmp_path, path)
