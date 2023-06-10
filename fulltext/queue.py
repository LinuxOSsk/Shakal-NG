# -*- coding: utf-8 -*-
import contextvars


_fulltext_queue_context = contextvars.ContextVar('fulltext_queue_context')


def enqueue_fulltext_update(object_ids, content_type):
	if not isinstance(object_ids, list):
		object_ids = [object_ids]

	queue = _fulltext_queue_context.get({})
	queue.setdefault(content_type.pk, set())
	queue[content_type.pk] |= set(object_ids)
	_fulltext_queue_context.set(queue)


def get_and_clear_fulltext_queue():
	queue = _fulltext_queue_context.get({})
	if queue:
		_fulltext_queue_context.set({})
	return queue
