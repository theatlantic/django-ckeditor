import sys
import re
import urlparse

from django.conf import settings


def get_media_url(path):
    """
    Determine system file's media URL.
    """
    upload_prefix = getattr(settings, "CKEDITOR_UPLOAD_PREFIX", None)
    if upload_prefix:
        url = upload_prefix + path.replace(settings.CKEDITOR_UPLOAD_PATH, '')
    else:
        url = settings.MEDIA_URL + path.replace(settings.MEDIA_ROOT, '')

    # Remove multiple forward-slashes from the path portion of the url.
    # Break url into a list.
    url_parts = list(urlparse.urlparse(url))
    # Replace two or more slashes with a single slash.
    url_parts[2] = re.sub('\/+', '/', url_parts[2])
    # Reconstruct the url.
    return urlparse.urlunparse(url_parts)


re_spaces = re.compile(ur"\s+")


def combine_css_classes(*classes_args):
    fn_name = lambda: sys._getframe().f_back.f_code.co_name

    if len(classes_args) == 0:
        raise TypeError(
            "%(fn_name)s takes 1 or more arguments (%(num)d given)" % {
                "fn_name": fn_name(),
                "num": len(classes_args),
            })
    new_classes = set([])
    for arg_pos, classes in enumerate(classes_args):
        if isinstance(classes, basestring):
            classes = set(re_spaces.split(classes.strip()))
        else:
            try:
                classes = set(classes)
            except TypeError:
                raise TypeError((
                    "%(fn_name)s argument %(arg_pos)s must be %(req_type)s, "
                    "not %(actual_type)s") % {
                        "fn_name": fn_name(),
                        "arg_pos": arg_pos + 1,
                        "req_type": "basestring or enumerable",
                        "actual_type": type(classes).__name__,
                    })
        new_classes.update(classes)
    return u" ".join(new_classes)
