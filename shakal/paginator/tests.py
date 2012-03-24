from django.test import TestCase
from paginator import Paginator

class PaginatorTest(TestCase):
	def test_01_init(self):
		paginator = Paginator(1, 10, inside = 10, outside = 20, raises_404 = True)
		self.assertEqual(paginator.page_count, 10)
		self.assertEqual(paginator.inside, 10)
		self.assertEqual(paginator.outside, 20)
		self.assertEqual(paginator.raises_404, True)

	def test_02_start(self):
		paginator = Paginator(1, 10, inside = 5, outside = 2, raises_404 = False)
		self.assertEqual(paginator.pages, [1, 2, 3, 4, 5, None, 9, 10])
		self.assertEqual(paginator.next, 2)
		self.assertEqual(paginator.previous, None)
		paginator = Paginator(1, 10, inside = 3, outside = 10, raises_404 = False)
		self.assertEqual(paginator.pages, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

	def test_03_end(self):
		paginator = Paginator(10, 10, inside = 5, outside = 2, raises_404 = False)
		self.assertEqual(paginator.pages, [1, 2, None, 6, 7, 8, 9, 10])
		self.assertEqual(paginator.next, None)
		self.assertEqual(paginator.previous, 9)

	def test_04_middle(self):
		paginator = Paginator(10, 20, inside = 5, outside = 2, raises_404 = False)
		self.assertEqual(paginator.pages, [1, 2, None, 8, 9, 10, 11, 12, None, 19, 20])
		self.assertEqual(paginator.next, 11)
		self.assertEqual(paginator.previous, 9)

	def test_05_border(self):
		paginator = Paginator(3, 10, inside = 5, outside = 2, raises_404 = False)
		self.assertEqual(paginator.pages, [1, 2, 3, 4, 5, None, 9, 10])
		paginator = Paginator(4, 10, inside = 5, outside = 2, raises_404 = False)
		self.assertEqual(paginator.pages, [1, 2, 3, 4, 5, 6, None, 9, 10])
		paginator = Paginator(7, 10, inside = 5, outside = 2, raises_404 = False)
		self.assertEqual(paginator.pages, [1, 2, None, 5, 6, 7, 8, 9, 10])
		paginator = Paginator(8, 10, inside = 5, outside = 2, raises_404 = False)
		self.assertEqual(paginator.pages, [1, 2, None, 6, 7, 8, 9, 10])

	def test_06_space(self):
		# Odstranenie medzier pri neparnom inside
		paginator = Paginator(5, 10, inside = 5, outside = 2, raises_404 = False)
		self.assertEqual(paginator.pages, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
		paginator = Paginator(5, 11, inside = 5, outside = 2, raises_404 = False)
		self.assertEqual(paginator.pages, [1, 2, 3, 4, 5, 6, 7, None, 10, 11])

		paginator = Paginator(5, 10, inside = 4, outside = 2, raises_404 = False)
		self.assertEqual(paginator.pages, [1, 2, 3, 4, 5, 6, 7, None, 9, 10])

