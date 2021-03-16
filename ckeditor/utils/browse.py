import os

from ckeditor import settings as ck_settings
from .common import get_media_url
from .image_upload import get_thumb_filename


def get_image_files(user=None):
    """
    Recursively walks all dirs under upload dir and generates a list of
    full paths for each file found.
    """
    # If a user is provided and CKEDITOR_RESTRICT_BY_USER is True,
    # limit images to user specific path, but not for superusers.
    if user and not user.is_superuser and ck_settings.RESTRICT_BY_USER:
        user_path = user.username
    else:
        user_path = ''

    browse_path = os.path.join(ck_settings.UPLOAD_PATH, user_path)

    for root, dirs, files in os.walk(browse_path):
        for filename in [os.path.join(root, x) for x in files]:
            # bypass for thumbs
            if os.path.splitext(filename)[0].endswith('_thumb'):
                continue
            yield filename


def get_image_browse_urls(user=None):
    """
    Recursively walks all dirs under upload dir and generates a list of
    thumbnail and full image URL's for each file found.
    """
    images = []
    for filename in get_image_files(user=user):
        images.append({
            'thumb': get_media_url(get_thumb_filename(filename)),
            'src': get_media_url(filename)
        })

    return images
