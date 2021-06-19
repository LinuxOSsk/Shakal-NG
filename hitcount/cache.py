# -*- coding: utf-8 -*-
from common_utils.cache import ObjectCache


class HitCountCache(ObjectCache):
	def set_hitcount(self, object_id, content_type_id, count):
		self.cache[object_id, content_type_id] = count
		self.save()


cache = HitCountCache('hitcount_cache')
