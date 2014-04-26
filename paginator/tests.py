# -*- coding: utf-8 -*-
from django.test import TestCase
from .paginator import Paginator


class PaginatorTest(TestCase):
	def test_on_start(self):
		paginator = Paginator(object_list=list(range(10)), inside=5, outside=2, per_page=1)
		page = paginator.page(1)
		self.assertEqual(page.page_range, [1, 2, 3, 4, 5, None, 9, 10])
		self.assertTrue(page.has_next())
		self.assertFalse(page.has_previous())
		self.assertEqual(page.next_page_number(), 2)
		paginator = Paginator(object_list=list(range(10)), inside=3, outside=10, per_page=1)
		page = paginator.page(1)
		self.assertEqual(page.page_range, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

	def test_on_end(self):
		paginator = Paginator(object_list=list(range(10)), inside=5, outside=2, per_page=1)
		page = paginator.page(10)
		self.assertEqual(page.page_range, [1, 2, None, 6, 7, 8, 9, 10])
		self.assertFalse(page.has_next())
		self.assertTrue(page.has_previous())
		self.assertEqual(page.previous_page_number(), 9)

	def test_middle(self):
		paginator = Paginator(object_list=list(range(20)), inside=5, outside=2, per_page=1)
		page = paginator.page(10)
		self.assertEqual(page.page_range, [1, 2, None, 8, 9, 10, 11, 12, None, 19, 20])
		self.assertTrue(page.has_next())
		self.assertTrue(page.has_previous())
		self.assertEqual(page.previous_page_number(), 9)
		self.assertEqual(page.next_page_number(), 11)

	def test_border(self):
		paginator = Paginator(object_list=list(range(10)), inside=5, outside=2, per_page=1)
		page = paginator.page(3)
		self.assertEqual(page.page_range, [1, 2, 3, 4, 5, None, 9, 10])
		paginator = Paginator(object_list=list(range(10)), inside=5, outside=2, per_page=1)
		page = paginator.page(4)
		self.assertEqual(page.page_range, [1, 2, 3, 4, 5, 6, None, 9, 10])
		paginator = Paginator(object_list=list(range(10)), inside=5, outside=2, per_page=1)
		page = paginator.page(7)
		self.assertEqual(page.page_range, [1, 2, None, 5, 6, 7, 8, 9, 10])
		paginator = Paginator(object_list=list(range(10)), inside=5, outside=2, per_page=1)
		page = paginator.page(8)
		self.assertEqual(page.page_range, [1, 2, None, 6, 7, 8, 9, 10])

	def test_space(self):
		paginator = Paginator(object_list=list(range(10)), inside=5, outside=2, per_page=1)
		page = paginator.page(5)
		self.assertEqual(page.page_range, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
		paginator = Paginator(object_list=list(range(11)), inside=5, outside=2, per_page=1)
		page = paginator.page(5)
		self.assertEqual(page.page_range, [1, 2, 3, 4, 5, 6, 7, None, 10, 11])

		paginator = Paginator(object_list=list(range(10)), inside=4, outside=2, per_page=1)
		page = paginator.page(5)
		self.assertEqual(page.page_range, [1, 2, 3, 4, 5, 6, 7, None, 9, 10])
