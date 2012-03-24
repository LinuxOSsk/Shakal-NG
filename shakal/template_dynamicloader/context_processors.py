from django.conf import settings
from shakal.template_dynamicloader.settings import TEMPLATE_DEFAULT_SKIN, TEMPLATE_DEFAULT_DEVICE

def templatepath(request):
	try:
		template_device = request.session['template_device']
	except KeyError:
		template_device = TEMPLATE_DEFAULT_DEVICE;

	try:
		template_skin = request.session['template_skin']
	except KeyError:
		template_skin = TEMPLATE_DEFAULT_SKIN;

	return {"template_static_path": template_device + '/' + template_skin}
