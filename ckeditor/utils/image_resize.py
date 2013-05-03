import os
import sys
import urlparse
import re
import hashlib
import logging

from lxml import html
from PIL import Image, ImageFile

from django.conf import settings
from django.contrib import messages
from ckeditor import settings as ck_settings
from .common import get_media_url


ImageFile.MAXBLOCKS = 10000000

logger = logging.getLogger(__name__)

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
    url = urlparse.unquote(url)
    local_path = settings.STATIC_ROOT + os.path.normpath(url[len(settings.STATIC_URL):])
    return local_path

# `buffer` is needed since hashlib apparently isn't unicode safe
hexhash = lambda s: hashlib.md5(buffer(s)).hexdigest()

def new_rendered_path(orig_path, width, height, ext=None):
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

    @param ext: Desired extension of the new image.  If None, uses 
                the original extension.
    @type  ext: basestring or None

    @return: Absolute path to where the rendered image should live.
    @rtype:  "/path/to/rendered/image"
    """
    dirname = os.path.dirname(orig_path)
    rendered_path = os.path.join(dirname, 'rendered')
    if not os.path.exists(rendered_path):
        os.mkdir(rendered_path)

    hash_path = hexhash(orig_path)

    if ext is None:
        ext = os.path.splitext(os.path.basename(orig_path))[1]
    if ext and ext[0] != u'.':
        ext = u'.' + ext

    name = '%s_%sx%s' % (hash_path, width, height)
    return os.path.join(rendered_path, name) + ext

def is_rendered(path, width, height):
    """
    Checks whether or not an image has been rendered to the given path
    with the given dimensions

    @param path: path to check
    @type  path: u"/path/to/image"
    
    @param width: Desired width
    @type  width: int
    
    @param height: Desired height
    @type  height: int

    @return: Whether or not the image is correct
    @rtype: bool
    """
    if os.path.exists(path):
        old_width, old_height = Image.open(path).size
        return old_width == width and old_height == height
    return False

def transcode_to_jpeg(image, path, width, height):
    """
    Transcodes an image to JPEG.

    @param image: Opened image to transcode to jpeg.
    @type  image: PIL.Image
    
    @param path: Path to the opened image.
    @type  path: u"/path/to/image"
    
    @param width: Desired width of the transcoded image.
    @type  width: int
    
    @param height: Desired height of the transcoded image.
    @type  height: int

    @return: Path to the new transcoded image.
    @rtype: "/path/to/image"
    """

    i_width, i_height = image.size
    new_width = i_width if width is None else width
    new_height = i_height if height is None else height

    new_path = new_rendered_path(path, width, height, ext='jpg')
    if is_rendered(new_path, new_width, new_height):
        return new_path

    new_image = image.resize((new_width, new_height), Image.ANTIALIAS)
    new_image.save(new_path, quality=80, optimize=1)
    return new_path


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
    # We have to call image.load first due to a PIL 1.1.7 bug 
    image.load()

    if image.format == 'PNG' and ck_settings.PNG_TO_JPEG:
        pixels = reduce(lambda a,b: a*b, image.size)
        # check that our entire alpha channel is set to full opaque
        if image.mode == 'RGB' or image.split()[-1].histogram()[-1] == pixels:
            return transcode_to_jpeg(image, path, width, height)
            
    if image.size <= (width, height):
        return path
    if width is None or height is None:
        return path

    # We can't resize animated gifs
    if image.format == 'GIF':
        try:
            image.seek(1)
            return path
        except EOFError:
            # Static GIFs should throw an EOF on seek
            pass

    # We can't resize gifs with transparency either
    if image.format == 'GIF' and image.info.get('transparency'):
        return path

    new_path = new_rendered_path(path, width, height)
    if is_rendered(new_path, width, height):
        return new_path

    # Re-render the image, optimizing for filesize
    new_image = image.resize((width, height), Image.ANTIALIAS)

    image_params = {}
    if image.format != "GIF":
        image_params = dict(
            quality = 80,
            optimize = 1,
        )
    new_image.save(new_path, **image_params)
    return new_path

def get_html_tree(content):
    return html.fragment_fromstring(content, create_parent='div')

def render_html_tree(tree):
    return html.tostring(tree)[5:-6]

def resize_images(post_content, request=None):
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
        try:
            rendered_path = re_render(orig_path, width, height)
        except Exception as e:
            # If something goes wrong, just use the original path so as not to
            # interrupt the user. However, log it and give them a warning.
            logger.warning(e, exc_info=True, extra={
                'stack': True,
            })

            if request:
                msg = "We had a problem resizing {img} to {x}x{y}".format(
                        img=os.path.split(orig_path)[1],
                        x=width,
                        y=height,
                    )
                messages.add_message(request, messages.WARNING, msg)
            
            continue  # Nevermind for now

        # If we haven't changed the image, move along.
        if rendered_path == orig_path:
            continue



        # Flip to the rendered
        img.attrib['data-original'] = orig_url
        img.attrib['src'] = get_media_url(rendered_path)

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
