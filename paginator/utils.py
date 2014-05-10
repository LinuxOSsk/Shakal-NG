# -*- coding: utf-8 -*-
from django.core.paginator import InvalidPage
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from .paginator import Paginator


def paginate_queryset(queryset, page, page_size):
	paginator = Paginator(queryset, page_size)
	try:
		page_number = int(page)
	except ValueError:
		raise Http404(_("Page is not number."))

	try:
		page = paginator.page(page_number)
		return (paginator, page, page.object_list, page.has_other_pages())
	except InvalidPage as e:
		raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {'page_number': page_number, 'message': str(e)})
