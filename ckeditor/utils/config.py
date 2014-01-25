import copy
import collections

import json
import json.encoder
from json.encoder import encode_basestring, encode_basestring_ascii, FLOAT_REPR
try:
    from json.encoder import _make_iterencode, c_make_encoder
except ImportError:
    # python 2.6
    _make_iterencode = c_make_encoder = None

from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_unicode
from django.utils.functional import Promise

from ckeditor import JSCode, settings as ck_settings


UNDEFINED_CONF = 'undef-config'
UNDEFINED_CONF_KEY = 'undef-config-setting'
INVALID_CONF_TYPE = 'invalid-config-type'
INVALID_CONF_KEY_TYPE = 'invalid-config-setting-type'


error_msgs = {
    UNDEFINED_CONF:        "CKEDITOR_CONFIGS not defined in settings",
    UNDEFINED_CONF_KEY:    "No configuration named '{conf}' found in"
                           " CKEDITOR_CONFIGS setting.",
    INVALID_CONF_TYPE:     "CKEDITOR_CONFIGS setting must be an instance"
                           " of collections.Mapping (e.g. dict), instead "
                           " found {type}",
    INVALID_CONF_KEY_TYPE: "CKEDITOR_CONFIGS['{conf}'] setting must be an"
                           " instance of collections.Mapping (e.g. dict),"
                           " instead found {type}",
}


def validate_config(config_name='default', config=None, instance=None):
    new_config = copy.deepcopy(ck_settings.DEFAULT_CONFIG)

    if config_name:
        if not ck_settings.CONFIGS:
            raise ImproperlyConfigured(error_msgs[UNDEFINED_CONF])
        if not isinstance(ck_settings.CONFIGS, collections.Mapping):
            raise ImproperlyConfigured(error_msgs[INVALID_CONF_TYPE].format(
                    type=type(ck_settings.CONFIGS).__name__))

        named_config = ck_settings.CONFIGS.get(config_name, None)

        if not named_config:
            raise ImproperlyConfigured(
                error_msgs[UNDEFINED_CONF_KEY].format(conf=config_name))

        if not isinstance(named_config, collections.Mapping):
            raise ImproperlyConfigured(
                error_msgs[INVALID_CONF_KEY_TYPE].format(
                    conf=config_name,
                    type=type(named_config).__name__))

        new_config.update(named_config)

    if config:
        new_config.update(config)
    return new_config


class LazyEncoder(json.JSONEncoder):

    def iterencode(self, o, _one_shot=False):
        markers = {} if self.check_circular else None
        if self.ensure_ascii:
            _encoder = encode_basestring_ascii
        else:
            _encoder = encode_basestring

        def _encoder(o, _orig_encoder=_encoder, _encoding=self.encoding):
            if isinstance(o, JSCode):
                return o
            if _encoding != 'utf-8' and isinstance(o, str):
                o = o.decode(_encoding)
            return _orig_encoder(o)

        def floatstr(o, allow_nan=self.allow_nan, _repr=FLOAT_REPR, **kwargs):
            defaults = {}
            if hasattr(json.encoder, 'INFINITY'):
                defaults = {
                    '_inf': json.encoder.INFINITY,
                    '_neginf': -json.encoder.INFINITY,
                }
            kwargs.update(defaults)
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.
            if o != o:
                text = 'NaN'
            elif '_inf' in kwargs and o == kwargs['_inf']:
                text = 'Infinity'
            elif '_neginf' in kwargs and o == kwargs['_neginf']:
                text = '-Infinity'
            else:
                return _repr(o)
            if not allow_nan:
                raise ValueError("Out of range float values are not JSON "
                                 "compliant: %s" % repr(o))
            return text

        if _one_shot and c_make_encoder and not(self.indent or self.sort_keys):
            _iterencode = c_make_encoder(markers, self.default, _encoder,
                self.indent, self.key_separator, self.item_separator,
                self.sort_keys, self.skipkeys, self.allow_nan)
        elif _make_iterencode:
            _iterencode = _make_iterencode(markers, self.default, _encoder,
                self.indent, floatstr, self.key_separator,
                self.item_separator, self.sort_keys, self.skipkeys, _one_shot)
        else:
            return super(LazyEncoder, self).iterencode(o)

        return _iterencode(o, 0)

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return super(LazyEncoder, self).default(obj)


json_encode = LazyEncoder().encode
pretty_json_encode = LazyEncoder(indent=4).encode
