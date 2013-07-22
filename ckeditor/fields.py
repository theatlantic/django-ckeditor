from django.db import models
from django import forms

from ckeditor.widgets import CKEditorWidget
from ckeditor.utils.image_resize import resize_images


class RichModelFieldMixin(object):

    def __init__(self, *args, **kwargs):
        self.config_name = kwargs.pop("config_name", "default")
        self.dynamic_resize = kwargs.pop("dynamic_resize", False)
        self.extra_config = kwargs.pop('extra_config', {})
        super(RichModelFieldMixin, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': RichTextFormField,
            'config_name': self.config_name,
            'dynamic_resize': self.dynamic_resize,
            'extra_config': self.extra_config,
        }
        defaults.update(kwargs) # Adds request if it's there too
        return super(RichModelFieldMixin, self).formfield(**defaults)


class RichCharField(RichModelFieldMixin, models.CharField):
    pass


class RichTextField(RichModelFieldMixin, models.TextField):
    pass


class RichTextFormField(forms.CharField):

    def __init__(self, config_name='default', *args, **kwargs):
        self.dynamic_resize = kwargs.pop("dynamic_resize", False)
        self.extra_config = kwargs.pop('extra_config', {})
        kwargs.update({
            'widget': CKEditorWidget(config_name=config_name, config=self.extra_config),
        })
        self.request = kwargs.pop('request', None)
        super(RichTextFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(RichTextFormField, self).to_python(value)
        if self.dynamic_resize:
            value = resize_images(value, request=self.request)
        return value


try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], ["^ckeditor\.fields\.RichCharField"])
    add_introspection_rules([], ["^ckeditor\.fields\.RichTextField"])
