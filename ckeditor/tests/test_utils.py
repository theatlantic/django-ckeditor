import os
import mock
from unittest2 import TestCase
from ckeditor.utils import re_render
from PIL.Image import Image

class TestReRender(TestCase):

    @classmethod
    def setup_class(self):
        self.static_path = os.path.join(os.path.dirname(__file__), 'static')

    @mock.patch.object(Image, 'save')
    @mock.patch('ckeditor.utils.is_rendered')
    def test_opaque_gif(self, mock_is_rendered, mock_save_method):
        """ Opaque GIF's should be resized. """
        mock_is_rendered.return_value = False
        path = os.path.join(self.static_path, 'opaque.gif')
        new_path = re_render(path, 101, 101)

        assert new_path == mock_save_method.call_args[0][0]  # We should save the new path name, obviously
        assert {} == mock_save_method.call_args[1]  # No other params should be passed


    def test_transparent_gif(self):
        """ Rerender should not change gifs with transparency. """
        path = os.path.join(self.static_path, 'transparent.gif')
        new_path = re_render(path, 101, 101)
        assert path == new_path