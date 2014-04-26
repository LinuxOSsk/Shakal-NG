# -*- coding: utf-8 -*-
from django.core.paginator import Paginator as OrigPaginator, Page as OrigPage

from .settings import PAGINATOR_INSIDE_COUNT, PAGINATOR_OUTSIDE_COUNT


class Page(OrigPage):
	def __init__(self, *args, **kwargs):
		super(Page, self).__init__(*args, **kwargs)
		self.page_range = []
		self.next = None
		self.previous = None

		if self.paginator.inside % 2:
			removeNone = True
			self.paginator.inside = (self.paginator.inside - 1) / 2
		else:
			removeNone = False
			self.paginator.inside = self.paginator.inside / 2

		ranges = []
		ranges.append((1, min(self.paginator.num_pages, self.paginator.outside)))
		# Posun pri presahu stredu
		midFix = 0
		if self.number - self.paginator.inside < 1:
			midFix = 1 - (self.number - self.paginator.inside)
		if self.number + self.paginator.inside > self.paginator.num_pages:
			midFix = self.paginator.num_pages - (self.number + self.paginator.inside)
		ranges.append((max(self.number - self.paginator.inside + midFix, 1), min(self.number + self.paginator.inside + midFix, self.paginator.num_pages)))
		ranges.append((max(self.paginator.num_pages + 1 - self.paginator.outside, 1), (self.paginator.num_pages)))

		newRanges = []
		currentRange = None
		for r in ranges:
			# Preskakovanie prvého rozsahu
			if currentRange is None:
				currentRange = r
				continue
			# Spojenie
			if currentRange[1] >= r[0] - (2 if removeNone else 1):
				currentRange = (currentRange[0], r[1])
			else:
				newRanges.append(currentRange)
				currentRange = r

		if not currentRange is None:
			newRanges.append(currentRange)

		for r in newRanges:
			self.page_range += range(r[0], r[1] + 1)
			self.page_range.append(None)

		if self.page_range and self.page_range[-1] is None:
			self.page_range = self.page_range[0:-1]


class Paginator(OrigPaginator):
	def __init__(self, *args, **kwargs):
		self.inside = kwargs.pop("inside", PAGINATOR_INSIDE_COUNT)
		self.outside = kwargs.pop("outside", PAGINATOR_OUTSIDE_COUNT)
		super(Paginator, self).__init__(*args, **kwargs)

	def _get_page(self, *args, **kwargs):
		return Page(*args ,**kwargs)
