# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dozer import Dozer

from .wsgi import application


application = Dozer(application)
