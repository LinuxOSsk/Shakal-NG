from django.conf import settings
from template_dynamicloader.settings import TEMPLATE_DEFAULT_NAME, TEMPLATE_DEFAULT_DEVICE

def templatepath(request):
	try:
		template_device = request.session['template_device']
	except KeyError:
		template_device = TEMPLATE_DEFAULT_DEVICE;

	try:
		template_name = request.session['template_name']
	except KeyError:
		template_name = TEMPLATE_DEFAULT_NAME;

	return {"template_static_path": template_device + '/' + template_name}
