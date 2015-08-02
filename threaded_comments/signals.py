# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.dispatch import Signal


comment_was_flagged = Signal(providing_args=["comment", "flag", "created", "request"])
