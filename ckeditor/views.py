from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from . import utils
from . import settings as ck_settings


@csrf_exempt
def upload(request):
    """
    Uploads a file and send back its URL to CKEditor.

    TODO:
        Validate uploads
    """
    # Get the uploaded file from request.
    upload = request.FILES['upload']

    # Open output file in which to store upload.
    upload_filename = utils.get_upload_filename(upload.name, request.user)
    out = open(upload_filename, 'wb+')

    # Iterate through chunks and write to destination.
    for chunk in upload.chunks():
        out.write(chunk)
    out.close()

    url = utils.create_thumbnail(upload_filename)

    # Respond with Javascript sending ckeditor upload url.
    return HttpResponse("""
    <script type='text/javascript'>
        window.parent.CKEDITOR.tools.callFunction(%s, '%s');
    </script>""" % (request.GET['CKEditorFuncNum'], url))


def browse(request):
    return render_to_response('browse.html', RequestContext(request, {
        'images': utils.get_image_browse_urls(request.user),
    }))


def configs(request):
    merged_configs = {}
    if ck_settings.CONFIGS is not None:
        for config_name, config in ck_settings.CONFIGS.iteritems():
            merged_configs[config_name] = utils.validate_config(config_name)

    return render_to_response('ckeditor/configs.js', RequestContext(request, {
        'debug': ck_settings.CKEDITOR_DEBUG,
        'timestamp': ck_settings.TIMESTAMP,
        'merged_configs': utils.pretty_json_encode(merged_configs),
        'jquery_override_val': utils.json_encode(ck_settings.JQUERY_OVERRIDE_VAL),
    }), mimetype="application/x-javascript")


@csrf_exempt
def fb_upload(request):
    """
    A wrapper around django-filebrowser's file upload view. It returns a
    javascript function call to CKEDITOR.tools.callFunction(), which
    CKEDITOR expects.
    """
    try:
        import filebrowser
    except ImportError:
        raise Exception("Filebrowser not installed")

    upload_file_view = None

    try:
        from filebrowser.sites import site
    except ImportError:
        pass
    else:
        upload_file_view = site._upload_file

    if upload_file_view is None:
        try:
            from filebrowser.views import _upload_file
        except ImportError:
            raise Exception(
                "django-filebrowser must be version 3.3.0 or greater; "
                "currently at version %s" % filebrowser.VERSION)
        else:
            upload_file_view = _upload_file

    # Create a dict on the request object that will be modified by the
    # filebrowser_post_upload signal receiver in ckeditor/models.py
    fb_data = request._fb_data = {}

    # Call original view function.
    # Within this function, the filebrowser_post_upload signal will be sent,
    # and our signal receiver will add the filebrowser.base.FileObject
    # instance to request._fb_data["upload_file"]
    upload_file_view(request)

    upload_file = fb_data.get('upload_file')
    if not upload_file:
        return HttpResponse("Error uploading file")

    return HttpResponse("""
    <script type='text/javascript'>
        window.parent.CKEDITOR.tools.callFunction(%s, '%s');
    </script>""" % (request.GET['CKEditorFuncNum'], upload_file.url))
