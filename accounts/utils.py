# -*- coding: utf-8 -*-
import hashlib
from pathlib import Path

from PIL import Image, ImageFilter
from common_utils import get_meta
from django.apps import apps
from django.conf import settings
from django.core.cache import caches
from django.utils import timezone
from django.utils.dateparse import parse_datetime


MODELS = [
	'article.article',
	'blog.post',
	'forum.topic',
	'news.news',
	'tweets.tweet',
	'wiki.page',
]


AVATAR_IMAGES = {
	'male': (
		('background', 5),
		('face', 4),
		('clothes', 65),
		('mouth', 26),
		('hair', 36),
		('eye', 32),
	),
	'female': (
		('background', 5),
		('face', 4),
		('clothes', 59),
		('mouth', 17),
		('head', 33),
		('eye', 53),
	),
}


default_cache = caches['default']


def last_objects():
	objects_cache = default_cache.get('last_objects')
	if objects_cache is None:
		objects_cache = {}
		for model in MODELS:
			last = (apps.get_model(model).objects
				.order_by('-created')
				.values_list('pk', 'created')[:99])
			objects_cache[model] = list(reversed(last))
		default_cache.set('last_objects', objects_cache, 60)
	return objects_cache


def clear_last_objects_cache(sender, **kwargs):
	opts = get_meta(sender)
	if '.'.join((opts.app_label, opts.model_name)) not in MODELS:
		return
	default_cache.delete('last_objects')


def count_new(last_visited, visited_items):
	counts = {}
	for model, items in last_objects().items():
		count = None
		count = 0
		if model in last_visited:
			visited_date = parse_datetime(last_visited[model])
		else:
			visited_date = None
		visited_ids = set(visited_items.get(model, []))
		for pk, date in items:
			if (visited_date is None or date > visited_date) and not pk in visited_ids:
				count += 1
		counts[model] = count
	return counts


def update_last_visited(user, content_type):
	now = timezone.now()
	user_settings = user.user_settings
	user_settings.setdefault('last_visited', {})
	last_visited = user_settings['last_visited']
	if content_type:
		last_visited[content_type] = now
	for model_name in MODELS:
		last_visited.setdefault(model_name, now)
	user.user_settings = user_settings
	user.save()


def update_visited_items(user, content_type, object_id):
	user_settings = user.user_settings
	user_settings.setdefault('visited_items', {})
	visited_items = user_settings['visited_items']
	content_visited_items = set(visited_items.get(content_type, []))
	content_visited_items.add(object_id)
	content_visited_items = content_visited_items.intersection(set(i[0] for i in last_objects()[content_type]))
	user_settings['visited_items'][content_type] = list(content_visited_items)
	user.user_settings = user_settings
	user.save()


def get_count_new(user):
	user_settings = user.user_settings
	last_visited = user_settings.get('last_visited', {})
	visited_items = user_settings.get('visited_items', {})
	return count_new(last_visited, visited_items)


def generated_avatar(data):
	hash_str = hashlib.md5(data.encode('utf-8')).hexdigest()

	avatar_dirname = Path(f'CACHE/avatars/{hash_str[-2:]}')
	avatar_filename = hash_str[:8] + '.png'
	if (Path(settings.STATICFILES_DIRS[0]) / avatar_dirname / avatar_filename).exists():
		return (avatar_dirname / avatar_filename).as_posix()

	data_hash = int(hash_str, 16)
	sex = 'male' if bool(data_hash % 4) else 'female'
	data_hash = data_hash // 4
	avatar_recipe = AVATAR_IMAGES[sex]

	img = None
	for name, count in avatar_recipe:
		imgnum = (data_hash % count) + 1
		filename = Path(__file__).parent / '8biticon' / sex / f'{name}{imgnum}.png'
		data_hash = data_hash // count
		if img is None:
			img = Image.open(filename).convert('RGB')
			img = img.filter(ImageFilter.GaussianBlur(25))
			img = img.resize((48, 48), Image.Resampling.NEAREST)
		else:
			past = Image.open(filename).convert('RGBA')
			past = past.resize((40, 40), Image.Resampling.NEAREST)
			img.paste(past, (4, 7, 44, 47), past)

	static_dir = Path(settings.STATICFILES_DIRS[0])
	(static_dir / avatar_dirname).mkdir(parents=True, exist_ok=True)
	img.save(static_dir / avatar_dirname / avatar_filename)

	if hasattr(settings, 'STATIC_ROOT'):
		static_root = Path(settings.STATIC_ROOT)
		(static_root / avatar_dirname).mkdir(parents=True, exist_ok=True)
		img.save(static_root / avatar_dirname / avatar_filename)
	return (avatar_dirname / avatar_filename).as_posix()
