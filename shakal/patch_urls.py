# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import urls
from django.contrib.syndication.views import Feed
from django.views.generic import View


class ClassBasedViewURLPattern(urls.RegexURLPattern):
	@property
	def callback(self):
		view = super(ClassBasedViewURLPattern, self).callback
		if isinstance(view, type):
			if issubclass(view, View):
				view = view.as_view(**self.default_args)
				self.default_args = {}
			elif issubclass(view, Feed):
				view = view(**self.default_args)
				self.default_args = {}
		return view


def patch_urls():
	urls.RegexURLPattern = ClassBasedViewURLPattern
