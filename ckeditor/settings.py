from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.functional import lazy


def url_reverse(pattern):
	return reverse(pattern)


lazy_reverse = lazy(reverse, str)


DEFAULT_CONFIG = {
    'skin': 'django',
    'toolbar': 'Full',
    'height': 291,
    'width': 835,
    'autoUpdateElement': True,
    'filebrowserWindowWidth': 940,
    'filebrowserWindowHeight': 725,
    'filebrowserUploadUrl': lazy_reverse('ckeditor_upload'),
    'filebrowserBrowseUrl': lazy_reverse('ckeditor_browse'),
}

JQUERY_OVERRIDE_VAL = getattr(settings, 'CKEDITOR_JQUERY_OVERRIDE_VAL', True)
