# -*- coding: utf-8 -*-
from django.contrib.postgres.indexes import PostgresIndex


class RumIndex(PostgresIndex):
	suffix = 'rum'
