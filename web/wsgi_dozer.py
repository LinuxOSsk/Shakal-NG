# -*- coding: utf-8 -*-
from dozer import Dozer

from .wsgi import application


application = Dozer(application)
