from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape

from django.forms.util import flatatt

from . import settings as ck_settings, utils


class CKEditorWidget(forms.Textarea):
    """
    Widget providing CKEditor for Rich Text Editing.
    Supports direct image uploads and embed.
    """

    #: space-separated list of css classes applied to the ckeditor textarea
    ckeditor_classes = ("django-ckeditor-textarea",)

    def __init__(self, config_name=None, config=None, attrs=None):
        super(CKEditorWidget, self).__init__(attrs)
        # Setup config from defaults.
        self.config_name = config_name
        self.extra_config = config
        self.config = utils.validate_config(config_name=config_name, config=config)

    @property
    def media(self):
        media_prefix = ck_settings.MEDIA_PREFIX
        if len(media_prefix) and media_prefix[-1] != '/':
            media_prefix += '/'
        source_dir = '%sckeditor/ckeditor' % media_prefix

        timestamp = ck_settings.TIMESTAMP

        if ck_settings.CKEDITOR_DEBUG:
            source_dir = "%s-dev" % source_dir

        media = super(CKEditorWidget, self).media
        media.add_js([
            '%s/ckeditor.js?timestamp=%s' % (source_dir, timestamp),
            reverse('ckeditor_configs'),
            '%s/core/adapters/jquery.js?timestamp=%s' % (source_dir, timestamp),
            '%s/ckeditor_widget.js?timestamp=%s' % (source_dir, timestamp),
        ])
        return media

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        value = utils.swap_in_originals(value)

        attrs = attrs or {}

        classes = attrs.pop('class', [])
        attrs['class'] = utils.combine_css_classes(classes, self.ckeditor_classes)
        if self.config_name:
            attrs['data-config-name'] = self.config_name
        if self.extra_config:
            attrs['data-config'] = utils.json_encode(self.extra_config)

        return mark_safe(u'<textarea%(attrs)s>%(value)s</textarea>' % {
            'attrs': flatatt(self.build_attrs(attrs, name=name)),
            'value': conditional_escape(force_unicode(value)),
        })
