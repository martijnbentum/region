from django.contrib.auth.decorators import permission_required
# from django.utils.translation import ugettext_lazy as _
import os
import mimetypes
from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy


def protected_media(request, filename):
	"""
	View to send file via X-Sendfile
	:param request: the HTTP request
	:param filename: the filename, extracted from the url
	:return: a HttpResponse object
	"""
	print(filename,'filename')
	# Construct full path and base name
	full_path = os.path.join(settings.MEDIA_ROOT, filename)
	base_name = os.path.basename(filename)

	# Check whether the file exist
	if not os.path.exists(full_path):
		# raise Http404(_("The requested file does not exist"))
		raise Http404("The requested file does not exist")

	# Let Django serve it if the XSENDFILE setting is false
	if not settings.XSENDFILE:
		from django.views.static import serve
		return serve(request, full_path, document_root='/')

	# Determine the mime type
	(mime_type, encoding) = mimetypes.guess_type(full_path)

	# Construct the response
	response = HttpResponse(content_type=mime_type)
	response['Content-Disposition'] = 'inline;filename='+base_name
	response['X-Sendfile'] = full_path

	return response 
