# -*- coding: utf-8 -*-
import logging
import unicodedata

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q, F, Value as V

from .models import SearchIndex
from .queue import enqueue_fulltext_update, get_and_clear_fulltext_queue
from .registry import register as fulltext_register
from comments.models import Comment


logger  = logging.getLogger(__name__)


def bulk_update(items):
	pks = [item.object_id for item in items]
	existing = dict(SearchIndex.objects.filter(content_type_id=items[0].content_type_id, object_id__in=pks).values_list('object_id', 'pk'))
	to_create = []
	to_update = []
	for item in items:
		pk = existing.get(item.object_id)
		if pk is None:
			to_create.append(item)
		else:
			item.pk = pk
			to_update.append(item)
	if to_create:
		SearchIndex.objects.bulk_create(to_create, ignore_conflicts=True)
	if to_update:
		SearchIndex.objects.bulk_update(to_update, fields=['created', 'updated', 'author', 'authors_name', 'title', 'document', 'comments', 'language_code'])
	SearchIndex.objects.filter(content_type_id=items[0].content_type_id, object_id__in=pks).update_search_index()


def search_simple(term, search_document=True, search_comments=True, content_types=None):
	if search_document is None and search_comments is None:
		return SearchIndex.objects.none()
	q = Q()
	term = term.split()
	if search_document:
		document_q = Q()
		for t in term:
			document_q &= Q(document__icontains=t)
		q |= document_q
	if search_comments:
		comments_q = Q()
		for t in term:
			comments_q &= Q(comments__icontains=t)
		q |= comments_q
	if content_types is not None:
		q = q & Q(content_type__in=content_types)
	return (SearchIndex.objects
		.filter(q)
		.annotate(rank=V(1.0, output_field=models.FloatField()))
		.only('content_type', 'object_id', 'language_code', 'created', 'updated', 'author', 'authors_name', 'title')
	)


def unaccent(text):
	nfkd_form = unicodedata.normalize('NFKD', text)
	return nfkd_form.encode('ASCII', 'ignore').decode()


def search_postgres(term, search_document=True, search_comments=True, content_types=None):
	from django.contrib.postgres.search import SearchQuery, SearchRank, SearchHeadline

	if search_document is None and search_comments is None:
		return SearchIndex.objects.none()
	term = unaccent(term)
	query = SearchQuery(term, config=settings.LANGUAGE_CODE, search_type='websearch')
	field = 'combined_search_vector'
	if not search_document:
		field = 'comments_search_vector'
	if not search_comments:
		field = 'document_search_vector'

	rank = SearchRank(F(field), query)
	highlights = {}
	for f in ['title', 'document', 'comments']:
		if f == 'document' and not search_document:
			continue
		if f == 'comments' and not search_comments:
			continue
		highlights['highlighted_' + f] = SearchHeadline(
			f,
			query,
			config=F('language_code'),
			start_sel=SearchIndex.HIGHLIGHT_START,
			stop_sel=SearchIndex.HIGHLIGHT_STOP,
			highlight_all=True
		)
	fields = {field: query}
	if content_types is not None:
		fields['content_type__in'] = content_types
	return (SearchIndex.objects
		.filter(**fields)
		.annotate(rank=rank, **highlights)
		.only('content_type', 'object_id', 'language_code', 'created', 'updated', 'author', 'authors_name', 'title')
		.order_by('-rank'))


def iterate_qs(qs, batch_size):
	last_pk = None
	while True:
		limited = qs.order_by('pk')
		if last_pk is not None:
			limited = limited.filter(pk__gt=last_pk)
		empty = True
		for item in limited[:batch_size]:
			last_pk = item.pk
			empty = False
			yield item
		if empty:
			break


def schedule_change_fulltext(sender, instance):
	search_indexes = fulltext_register.get_for_model(sender)

	if search_indexes:
		content_type = ContentType.objects.get_for_model(sender)
		enqueue_fulltext_update([instance.pk], content_type)

	# enqueue comments
	if sender is Comment:
		try:
			content_type = ContentType.objects.get_for_id(instance.content_type_id)
			search_indexes = fulltext_register.get_for_model(content_type.model_class())
			if search_indexes:
				enqueue_fulltext_update([instance.object_id], content_type)
		except ContentType.DoesNotExist:
			pass


def schedule_update_fulltext(sender, instance, **kwargs):
	schedule_change_fulltext(sender, instance)


def schedule_delete_fulltext(sender, instance, **kwargs):
	schedule_change_fulltext(sender, instance)


def perform_update_fulltext(sender, **kwargs): # pylint: disable=unused-argument
	scheduled = get_and_clear_fulltext_queue()
	if not scheduled:
		return

	from .api import update_search_index

	try:
		for content_type_id, id_list in scheduled.items():
			content_type = ContentType.objects.get_for_id(content_type_id)
			search_indexes = fulltext_register.get_for_model(content_type.model_class())
			for Index in search_indexes:
				update_search_index(Index(), update_ids=id_list)
	except Exception:
		logger.exception("Fulltext not updated")
