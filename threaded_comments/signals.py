# -*- coding: utf-8 -*-
from django.dispatch import Signal

comment_was_flagged = Signal(providing_args=["comment", "flag", "created", "request"])
