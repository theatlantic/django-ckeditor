"""
Validation logic, to be run on initialization of django models
"""
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if 'ckeditor' in settings.INSTALLED_APPS:
    # Confirm CKEDITOR_UPLOAD_PATH setting has been specified.
    try:
        settings.CKEDITOR_UPLOAD_PATH
    except AttributeError:
        raise ImproperlyConfigured("django-ckeditor requires \
                CKEDITOR_UPLOAD_PATH setting. This setting specifies an \
                absolute path to your ckeditor media upload directory. Make \
                sure you have write permissions for the path, i.e.: \
                CKEDITOR_UPLOAD_PATH = '/home/media/media.lawrence.com/\
                uploads'")

    # If a CKEDITOR_UPLOAD_PATH settings has been specified, confirm it exists.
    if getattr(settings, 'CKEDITOR_UPLOAD_PATH', None):
        if not os.path.exists(settings.CKEDITOR_UPLOAD_PATH):
            raise ImproperlyConfigured("django-ckeditor CKEDITOR_UPLOAD_PATH \
                    setting error, no such file or directory: '%s'" % \
                    settings.CKEDITOR_UPLOAD_PATH)


# Connect to django-filebrowser's filebrowser_post_upload signal.
# This is the only way to get the uploaded file's location into
# ckeditor.views.fb_upload when wrapping a call to the filebrowser's
# file upload view function.

filebrowser_post_upload = None

try:
    # django-filebrowser >= 3.5.0
    from filebrowser.signals import filebrowser_post_upload
except ImportError:
    try:
        # django-filebrowser <= 3.4.x
        from filebrowser.views import filebrowser_post_upload
    except ImportError:
        pass

if filebrowser_post_upload:
    def post_upload_callback(sender, **kwargs):
        request = sender
        upload_file = kwargs.get('file')
        if not upload_file:
            return
        fb_data = getattr(request, '_fb_data', None)
        if not isinstance(fb_data, dict):
            return
        fb_data['upload_file'] = upload_file
    filebrowser_post_upload.connect(post_upload_callback)
