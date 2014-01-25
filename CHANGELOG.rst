Changelog
=========

4.3.2
-----

* Updated to CKEditor 4.3.2
* Added source maps for the concatenated and minified javascript files
* Fixed bug that caused parse errors in JSON.parse (thanks `blag <https://github.com/blag>`_)
* Fixed ``django.conf.urls`` import for Django 1.5 (where it was deprecated) and Django 1.6
  (where it was removed).

4.3.0 beta
----------

* Updated to CKEditor 4.3.0 beta
* Added form clean method that strips control characters from input

4.1.2
-----

* Updated to CKEditor 4.1.2
* Added ``RichCharField``, which is functionally the same as ``RichTextField``, but is a django ``CharField``, not a ``TextField``
* Added ability to pass raw javascript into settings (e.g. javascript functions, conditional logic) with the ``JSCode`` class
* Changed ckeditor-dev folder to use the ckeditor repository and isolated custom javascript to allow easier version updates.

3.6.3
-----

* Forked from `shaunsephton <https://github.com/shaunsephton/django-ckeditor>`_
* Updated to CKEditor 3.6.3
* Automatic image resize functionality
* Support Promise objects in ``CKEDITOR_CONFIG`` (thanks `timheap <https://github.com/timheap>`_)
* Added ``CKEDITOR_DEBUG`` setting, which if set to ``True`` uses the unminified CKEditor javascript
* Support for django-filebrowser's file browser and uploader
* Added a ``config`` keyword argument to RichTextFields, which provides a way of defining or overriding
  configuration directly on a RichTextField without requiring an edit to the ``CKEDITOR_CONFIGS`` setting.

3.6.2
-----

* Include CKEditor version 3.6.2.
* Initial work on Django aligned theme. 
* Fix schema slash removal issue on media url generation. Thanks `mwcz <https://github.com/mwcz>`_
* Added compatibility for South. Thanks `3point2 <https://github.com/3point2>`_
* Prevented settings from leaking between widget instances. Thanks `3point2 <https://github.com/3point2>`_
* Fixed config_name conflict when verbose_name is used as first positional argument for a field. Thanks `3point2 <https://github.com/3point2>`_
* Refactored views to allow use of file walking with local paths. Thanks `3point2 <https://github.com/3point2>`_
* Added command to generate thumbnails. Thanks `3point2 <https://github.com/3point2>`_
* Migrated from using media to static file management.

0.0.9
-----

* Added ability to configure CKeditor through a CKEDITOR_CONFIGS settings. Thanks `jeffh <https://github.com/jeffh>`_ for the input.

0.0.8
-----

* Removed buggy url include check.

0.0.7
-----

* Egg package corrected to exclude testing admin.py and models.py.

0.0.6
-----

* Enforce correct configuration.
* Changed upload behavior to separate files into directories by upload date. Thanks `loop0 <http://github.com/loop0>`_ .
* Added ability to limit user access to uploaded content (see the CKEDITOR_RESTRICT_BY_USER setting). Thanks `chr15m <http://github.com/chr15m>`_ for the input.
* Added initial set of much needed tests.
* General cleanup, light refactor.

0.0.5
-----

* csrf_exempt backwards compatability. Thanks `chr15m <http://github.com/chr15m>`_ .

0.0.4
-----

* Include resources, sorry about that.

0.0.3
-----

* More robust PIL import. Thanks `buchuki <http://github.com/buchuki>`_ .
* Better CKEDITOR_MEDIA_PREFIX setting error.

0.0.2
-----

* Included README.rst in manifest.

0.0.1
-----

* Added CKEDITOR_UPLOAD_PREFIX setting. Thanks `chr15m <http://github.com/chr15m>`_ for the input.
