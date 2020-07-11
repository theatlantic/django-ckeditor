Django CKEditor
================

**Django admin CKEditor integration.**

Provides a ``RichTextField`` and ``CKEditorWidget`` utilizing CKEditor with image upload and browsing support included.

.. contents:: Contents
    :depth: 5

Testing
-------

Easiest::

    python3 -m venv venv
    . venv/bin/activate
    pip install tox
    tox

Other::

    python3 -m venv venv
    . venv/bin/activate
    python -m pip install "lxml==4.5.0" "mock==3.0.5" "Pillow==6.2.1" "Django>=2.0,<2.1"
    python setup.py test


Installation
------------

Required
~~~~~~~~

#. Install or add django-ckeditor to your python path.

#. Add ``ckeditor`` to your ``INSTALLED_APPS`` setting.

#. Run the ``collectstatic`` management command: ``manage.py collectstatic``. This'll copy static CKEditor require media resources into the directory given by the ``STATIC_ROOT`` setting. See `Django's documentation on managing static files <https://docs.djangoproject.com/en/dev/howto/static-files>`_ for more info.

#. Add a CKEDITOR_UPLOAD_PATH setting to the project's ``settings.py`` file. This setting specifies an absolute filesystem path to your CKEditor media upload directory. Make sure you have write permissions for the path, i.e.:

   .. code:: python

       CKEDITOR_UPLOAD_PATH = "/home/media/media.lawrence.com/uploads"

#. Add CKEditor URL include to your project's ``urls.py`` file:

   .. code:: python
    
       (r'^ckeditor/', include('ckeditor.urls')),    

Optional
~~~~~~~~

#. Set the CKEDITOR_RESTRICT_BY_USER setting to ``True`` in the project's ``settings.py`` file (default ``False``). This restricts access to uploaded images to the uploading user (e.g. each user only sees and uploads their own images). Superusers can still see all images. **NOTE**: This restriction is only enforced within the CKEditor media browser. 

#. Add a CKEDITOR_UPLOAD_PREFIX setting to the project's ``settings.py`` file. This setting specifies a URL prefix to media uploaded through CKEditor, i.e.:

   .. code:: python

       CKEDITOR_UPLOAD_PREFIX = "http://media.lawrence.com/media/ckuploads/

   (If CKEDITOR_UPLOAD_PREFIX is not provided, the media URL will fall back to MEDIA_URL with the difference of MEDIA_ROOT and the uploaded resource's full path and filename appended.)

#. Add a CKEDITOR_CONFIGS setting to the project's ``settings.py`` file. This specifies sets of CKEditor settings that are passed to CKEditor (see CKEditor's `Setting Configurations <http://docs.cksource.com/CKEditor_3.x/Developers_Guide/Setting_Configurations>`_), i.e.:

   .. code:: python

        CKEDITOR_CONFIGS = {
            'awesome_ckeditor': {
                'toolbar': 'Basic',
            },
        }

   The name of the settings can be referenced when instantiating a RichTextField:

   .. code:: python

        content = RichTextField(config_name='awesome_ckeditor')

   The name of the settings can be referenced when instantiating a CKEditorWidget:

   .. code:: python

        widget = CKEditorWidget(config_name='awesome_ckeditor')
   
   By specifying a set named ``default`` you'll be applying its settings to all RichTextField and CKEditorWidget objects for which ``config_name`` has not been explicitly defined:

   .. code:: python
       
       CKEDITOR_CONFIGS = {
           'default': {
               'toolbar': 'Full',
               'height': 300,
           'width': 300,
           },
       }

#. Add CKEDITOR_PNG_TO_JPEG setting to project's ``settings.py`` file.  This will convert all non-transparent PNG files to JPEG images instead, when ``dynamic_resize`` is set to ``True``.  This can save a large amount of bandwidth by reducing potentially large PNGs  to a more conservatively sized jpeg.


Usage
-----

Field
~~~~~

The quickest way to add rich text editing capabilities to your models is to use the included ``RichTextField`` model field type. A CKEditor widget is rendered as the form field but in all other regards the field behaves as the standard Django ``TextField``. For example:

.. code:: python

    from django.db import models
    from ckeditor.fields import RichTextField

    class Post(models.Model):
        content = RichTextField()

RichTextField takes an optional kwarg, ``dynamic_resize``, which attempts to optimize embeded images.  The default value is ``False``.

Admin
~~~~~

Our version of Django-CKEditor will create thumbnails of resized images on save. By default, if something goes wrong, it raises an exception. We prefer to pass a warning to the user (using messages), log the error, rather than stock saving and validation dead in its tracks.

To use this feature in the admin, add this to your ModelAdmin to ensure the form can access the request:

.. code:: python

    def formfield_for_dbfield(self, db_field, request=None, **kwargs):
        if isinstance(db_field, RichTextField):
            return db_field.formfield(request=request, **kwargs)
        return super(PostAdmin, self).formfield_for_dbfield(db_field, request=request, **kwargs)

Widget
~~~~~~

Alernatively you can use the included ``CKEditorWidget`` as the widget for a formfield. For example:

.. code:: python

    from django import forms
    from django.contrib import admin
    from ckeditor.widgets import CKEditorWidget

    from post.models import Post

    class PostAdminForm(forms.ModelForm):
        content = forms.CharField(widget=CKEditorWidget())
        class Meta:
            model = Post

    class PostAdmin(admin.ModelAdmin):
        form = PostAdminForm
    
    admin.site.register(Post, PostAdmin)

Managment Commands
~~~~~~~~~~~~~~~~~~

Included is a management command to create thumbnails for images already contained in ``CKEDITOR_UPLOAD_PATH``. This is useful to create thumbnails when starting to use django-ckeditor with existing images. Issue the command as follows::
    
    manage.py generateckeditorthumbnails

**NOTE**: If you're using custom views remember to include ckeditor.js in your form's media either through ``{{ form.media }}`` or through a ``<script>`` tag. Admin will do this for you automatically. See `Django's Form Media docs <http://docs.djangoproject.com/en/dev/topics/forms/media/>`_ for more info.

