from django.db.models.signals import pre_save
import ckeditor.utils as u

def add_dynamic_resize(cls, field_name):
    def _pre_signal(sender, instance, *args, **kwargs):
        field = getattr(instance, field_name, None)
        if field is None:
            return
        
        setattr(instance, field_name, u.resize_images(field))
        
    print "Binding dynamic resize"
    pre_save.connect(_pre_signal, sender=cls, weak=False)

    
