# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.utils.encoding import force_text


def create_json_response(data, **kwargs):
	body = force_text(json.dumps(data, cls=DjangoJSONEncoder))
	return HttpResponse(body, content_type="application/json", **kwargs)
