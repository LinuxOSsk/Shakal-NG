# -*- coding: utf-8 -*-
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.utils.encoding import force_str


def create_json_response(data, **kwargs):
	body = force_str(json.dumps(data, cls=DjangoJSONEncoder))
	return HttpResponse(body, content_type="application/json", **kwargs)
