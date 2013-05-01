import copy
import collections

import json
from django.utils.encoding import force_unicode
from django.utils.functional import Promise

from django.core.exceptions import ImproperlyConfigured

from ckeditor import settings as ck_settings


MISSING_KWARGS = 'missing-kwargs'
UNDEFINED_CONF = 'undef-config'
UNDEFINED_CONF_KEY = 'undef-config-setting'
INVALID_CONF_TYPE = 'invalid-config-type'
INVALID_CONF_KEY_TYPE = 'invalid-config-setting-type'


error_msgs = {
    MISSING_KWARGS:        "{cls_name} requires either 'config_name' or"
                           " 'config' keyword arguments",
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


def validate_config(config_name=None, config=None, instance=None):
    new_config = copy.deepcopy(ck_settings.DEFAULT_CONFIG)

    # Try to get valid config from settings.
    if config_name is None and config is None and instance:
        raise TypeError(error_msgs[MISSING_KWARGS].format(
                cls_name=instance.__class__.__name__))

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
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return super(LazyEncoder, self).default(obj)


json_encode = LazyEncoder().encode
pretty_json_encode = LazyEncoder(indent=4).encode
