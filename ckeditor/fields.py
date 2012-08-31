from django.db import models
from django import forms

import ckeditor.signals as signals
from ckeditor.widgets import CKEditorWidget


class RichTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.config_name = kwargs.pop("config_name", "default")
        self.dynamic_resize = kwargs.pop("dynamic_resize",False)
        super(RichTextField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': RichTextFormField,
            'config_name': self.config_name,
        }
        defaults.update(kwargs)
        return super(RichTextField, self).formfield(**defaults)

    def contribute_to_class(self, cls, name):
        super(RichTextField, self).contribute_to_class(cls, name)
        if self.dynamic_resize:
            signals.add_dynamic_resize(cls, name)

class RichTextFormField(forms.fields.Field):
    def __init__(self, config_name='default', *args, **kwargs):
        kwargs.update({'widget': CKEditorWidget(config_name=config_name)})
        super(RichTextFormField, self).__init__(*args, **kwargs)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^ckeditor\.fields\.RichTextField"])
except:
    pass
