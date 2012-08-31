import uuid
import os
import shutil
import urlparse
import re
import hashlib

from lxml import html
from PIL import Image, ImageFile

from django.conf import settings

import views
ImageFile.MAXBLOCKS = 10000000

def match_or_none(string, rx):
    """
    Tries to match a regular expression and returns an integer if it can.
    Otherwise, returns None.

    @param string: String to match against
    @type  string: basestring
    
    @param rx: compiled regular expression

    @return: number or None
    @rtype: int/long or None
    """
    if string is None:
        return None
    match = rx.search(string)
    if match:
        return int(match.groups()[0])
    return None

width_rx = re.compile(r'width\s*:\s*(\d+)(px)?')
height_rx = re.compile(r'height\s*:\s*(\d+)(px)?')
def get_dimensions(img):
    """
    Attempts to get the dimensions of an image from the img tag.
    It first tries to grab it from the css styles and then falls back
    to looking at the attributes.

    @param img: Image tag.
    @type  img: etree._Element

    @return: width and height of the image
    @rtype: (int or None, int or None)
    """
    styles = img.attrib.get('style')

    width = match_or_none(styles, width_rx) or img.attrib.get('width') 
    if isinstance(width, basestring):
        width = int(width)
    height = match_or_none(styles, height_rx) or img.attrib.get('height') 
    if isinstance(height, basestring):
        height= int(height)
    return width, height

def get_local_path(url):
    """
    Converts a url to a local path

    @param url: Url to convert
    @type  url: basestring

    @return: Local path of the url
    @rtype:  basestring
    """
    local_path = settings.STATIC_ROOT + url[len(settings.STATIC_URL):]
    return local_path

hexhash = lambda s: hashlib.md5(s).hexdigest()

def new_rendered_path(orig_path, width, height):
    """
    Builds a new rendered path based on the original path, width, and height.
    It takes a hash of the original path to prevent users from accidentally 
    (or purposely) overwritting other's rendered thumbnails.

    This isn't perfect: we are assuming that the original file's conents never 
    changes, which is the django default.  We could make this function more
    robust by hashing the file everytime we save but that has the obvious
    disadvantage of having to hash the file everytime.  YMMV.
    
    @param orig_path: Path to the original image.
    @type  orig_path: "/path/to/file"
    
    @param width: Desired width of the rendered image.
    @type  width: int or None
    
    @param height: Desired height of the rendered image.
    @type  height: int or None

    @return: Absolute path to where the rendered image should live.
    @rtype:  "/path/to/rendered/image"
    """
    dirname = os.path.dirname(orig_path)
    rendered_path = os.path.join(dirname, 'rendered')
    if not os.path.exists(rendered_path):
        os.mkdir(rendered_path)

    hash_path = hexhash(orig_path)

    ext = os.path.splitext(os.path.basename(orig_path))[1]
    name = '%s_%sx%s' % (hash_path, width, height)
    return os.path.join(rendered_path, name) + ext

def re_render(path, width, height):
    """
    Given an original image, width, and height, creates a thumbnailed image
    of the exact dimensions given.  We skip animated gifs because PIL can't
    resize those automatically whereas browsers can contort them easily.  We
    also don't stretch images at all and return the original in that case.

    @param path: Path to the original image
    @type  path: "/path/to/image"
    
    @param width: Desired width
    @type  width: int or None
    
    @param height: Desired height
    @type  height: int or None

    @return: Path to the 'rendered' image.
    @rtype:  "/path/to/image"
    """
    try:
        image = Image.open(path)
    except IOError:
        # Probably doesn't exist or isn't an image
        return path

    if image.size <= (width, height):
        return path
    if width is None and height is None:
        return path

    new_path = new_rendered_path(path, width, height)
    if os.path.exists(new_path):
        old_width, old_height = Image.open(new_path).size
        if old_width == width and old_height == height:
            return new_path

    # We can't resize animated gifs
    if image.format == 'GIF':
        try:
            image.seek(1)
            return path
        except EOFError:
            # Static GIFs should throw an EOF on seek
            pass
    
    # Re-render the image, optimizing for filesize
    new_image = image.resize((width, height), Image.ANTIALIAS)
    new_image.save(new_path, quality=80, optimize=1)
    return new_path

def get_html_tree(content):
    return html.fragment_fromstring(content, create_parent='div')

def render_html_tree(tree):
    return html.tostring(tree)[5:-6]

def resize_images(post_content):
    """
    Goes through all images, resizing those that we know to be local to the
    correct image size.

    @param post_content: Raw html of the content to search for images with.
    @type  post_content: basestring containg HTML fragments

    @return: Modified contents.
    @rtype:  basestring
    """
    # Get tree
    tree = get_html_tree(post_content)

    # Get images
    imgs = tree.xpath('//img[starts-with(@src, "%s")]' % settings.STATIC_URL)
    for img in imgs:
        orig_url = img.attrib['src']
        orig_path = get_local_path(orig_url)

        width, height = get_dimensions(img)
        rendered_path = re_render(orig_path, width, height)

        # If we haven't changed the image, move along.
        if rendered_path == orig_path:
            continue

        # Flip to the rendered
        img.attrib['data-original'] = orig_url
        img.attrib['src'] = views.get_media_url(rendered_path)

    # Strip of wrapping div tag
    return render_html_tree(tree)

def swap_in_originals(content):
    if 'data-original' not in content:
        return content
    
    tree = get_html_tree(content)
    for img in tree.xpath('//img[@data-original]'):
        img.attrib['src'] = img.attrib['data-original']
        del img.attrib['data-original']
    
    return render_html_tree(tree)
