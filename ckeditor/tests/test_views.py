import os
import unittest
from datetime import datetime

from django.conf import settings

from ckeditor import utils
from ckeditor import settings as ck_settings


class ViewsTestCase(unittest.TestCase):

    def setUp(self):
        # Retain original settings.
        TEST_MEDIA_ROOT = '/media/root/' # TODO: What is this?
        self.test_settings = {
            'MEDIA_ROOT': TEST_MEDIA_ROOT,
            'UPLOAD_PATH': os.path.join(TEST_MEDIA_ROOT, 'uploads'),
            'MEDIA_URL': '/media/',
        }

        self.orig_settings = {}
        for k, v in self.test_settings.iteritems():
            self.orig_settings[k] = v
            setattr(ck_settings, k, v)

        # Create dummy test upload path.
        self.test_path = os.path.join(ck_settings.UPLOAD_PATH, \
                'arbitrary', 'path', 'and', 'filename.ext')

        # Create mock user.
        self.mock_user = type('User', (object,), dict(username='test_user', \
                is_superuser=False))

    def tearDown(self):
        # Reset original settings.
        for k, v in self.test_settings.iteritems():
            setattr(ck_settings, k, self.orig_settings[k])

    def test_get_media_url(self):
        # If provided prefix URL with ck_settings.UPLOAD_PREFIX.
        ck_settings.UPLOAD_PREFIX = '/media/ckuploads/'
        prefix_url = '/media/ckuploads/arbitrary/path/and/filename.ext'
        self.failUnless(utils.get_media_url(self.test_path) == prefix_url)

        # If ck_settings.UPLOAD_PREFIX is not provided, the media URL will fall
        # back to MEDIA_URL with the difference of MEDIA_ROOT and the
        # uploaded resource's full path and filename appended.
        ck_settings.UPLOAD_PREFIX = None
        no_prefix_url = '/media/uploads/arbitrary/path/and/filename.ext'
        self.failUnless(utils.get_media_url(self.test_path) == no_prefix_url)

        # Resulting URL should never include '//' outside of schema.
        ck_settings.UPLOAD_PREFIX = 'https://test.com//media////ckuploads/'
        multi_slash_path = '//multi//////slash//path////'
        self.failUnlessEqual(
            'https://test.com/media/ckuploads/multi/slash/path/',
            utils.get_media_url(multi_slash_path))

    def test_get_thumb_filename(self):
        # Thumnbnail filename is the same as original
        # with _thumb inserted before the extension.
        self.failUnless(utils.get_thumb_filename(self.test_path) == \
                self.test_path.replace('.ext', '_thumb.ext'))
        # Without an extension thumnbnail filename is the same as original
        # with _thumb appened.
        no_ext_path = self.test_path.replace('.ext', '')
        self.failUnless(utils.get_thumb_filename(no_ext_path) == \
                no_ext_path + '_thumb')

    def test_get_image_browse_urls(self):
        ck_settings.MEDIA_ROOT = os.path.join(
            os.path.dirname(__file__), '../', 'media')
        ck_settings.UPLOAD_PATH = os.path.join(settings.MEDIA_ROOT, \
                'test_uploads')
        #ck_settings.RESTRICT_BY_USER = True

        # The test_uploads path contains subfolders, we should eventually reach
        # a single dummy resource.
        self.failUnless(utils.get_image_browse_urls())

        # Ignore thumbnails.
        self.failUnless(len(utils.get_image_browse_urls()) == 1)

        # Don't limit browse to user specific path if ck_settings.RESTRICT_BY_USER
        # is False.
        ck_settings.RESTRICT_BY_USER = False
        self.failUnless(len(utils.get_image_browse_urls(self.mock_user)) == 1)

        # Don't limit browse to user specific path if ck_settings.RESTRICT_BY_USER
        # is True but user is a superuser.
        ck_settings.RESTRICT_BY_USER = True
        self.mock_user.is_superuser = True
        self.failUnless(len(utils.get_image_browse_urls(self.mock_user)) == 1)

        # Limit browse to user specific path if ck_settings.RESTRICT_BY_USER is
        # True and user is not a superuser.
        ck_settings.RESTRICT_BY_USER = True
        self.mock_user.is_superuser = False
        self.failIf(utils.get_image_browse_urls(self.mock_user))

        ck_settings.RESTRICT_BY_USER = self.orig_settings["RESTRICT_BY_USER"]

    def test_get_upload_filename(self):
        ck_settings.UPLOAD_PATH = self.orig_settings["UPLOAD_PATH"]
        date_path = datetime.now().strftime('%Y/%m/%d')

        # Don't upload to user specific path if ck_settings.RESTRICT_BY_USER
        # is False.
        ck_settings.RESTRICT_BY_USER = False
        filename = utils.get_upload_filename('test.jpg', self.mock_user)
        self.failIf(filename.replace('/%s/test.jpg' % date_path, '').\
                endswith(self.mock_user.username))

        # Upload to user specific path if ck_settings.RESTRICT_BY_USER is True.
        ck_settings.RESTRICT_BY_USER = True
        filename = utils.get_upload_filename('test.jpg', self.mock_user)
        self.failUnless(filename.replace('/%s/test.jpg' % date_path, '').\
                endswith(self.mock_user.username))

        # Upload path should end in current date structure.
        filename = utils.get_upload_filename('test.jpg', self.mock_user)
        self.failUnless(filename.replace('/test.jpg', '').endswith(date_path))

        ck_settings.RESTRICT_BY_USER = self.orig_settings["RESTRICT_BY_USER"]
