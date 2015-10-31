# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys

import sass


compiled = sass.compile(string=open(sys.argv[1], 'r').read(), include_paths=(os.path.dirname(sys.argv[1]),))
open(os.path.splitext(sys.argv[1])[0] + '.css', 'w').write(compiled)
