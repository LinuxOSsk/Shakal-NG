# -*- coding: utf-8 -*-

from settings import PAGINATOR_INSIDE_COUNT, PAGINATOR_OUTSIDE_COUNT, PAGINATOR_RAISES_404

class Paginator:
	def __init__(self, current_page, page_count, inside = PAGINATOR_INSIDE_COUNT, outside = PAGINATOR_OUTSIDE_COUNT, raises_404 = PAGINATOR_RAISES_404):
		self.pages = []
		self.current_page = current_page
		self.page_count = page_count
		self.inside = inside
		self.outside = outside
		self.raises_404 = raises_404
		self.next = None
		self.previous = None

		if inside % 2:
			removeNone = True
			inside = (inside - 1) / 2
		else:
			removeNone = False
			inside = inside / 2

		ranges = []
		ranges.append((1, min(page_count, outside)))
		# Posun pri presahu stredu
		midFix = 0
		if current_page - inside < 1:
			midFix = 1 - (current_page - inside)
		if current_page + inside > page_count:
			midFix = page_count - (current_page + inside)
		ranges.append((max(current_page - inside + midFix, 1), min(current_page + inside + midFix, page_count)))
		ranges.append((max(page_count + 1 - outside, 1), (page_count)))

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
			self.pages += range(r[0], r[1] + 1)
			self.pages.append(None)

		if self.pages and self.pages[-1] is None:
			self.pages = self.pages[0:-1]

		if current_page < page_count:
			self.next = current_page + 1
		if current_page > 1:
			self.previous = current_page - 1

