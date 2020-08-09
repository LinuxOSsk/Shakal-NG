# -*- coding: utf-8 -*-
from django.db.models import Func


class Unaccent(Func):
	function = 'f_unaccent'
