from __future__ import absolute_import
try:
    from django.conf.urls import url
except ImportError:
    # Django <= 1.3
    from django.conf.urls.defaults import url

import ckeditor.views


urlpatterns = [
    url(r'^upload/', ckeditor.views.upload, name='ckeditor_upload'),
    url(r'^browse/', ckeditor.views.browse, name='ckeditor_browse'),
    url(r'^configs/', ckeditor.views.configs, name='ckeditor_configs'),
    url(r'^fb_upload/', ckeditor.views.fb_upload, name='ckeditor_fb_upload'),
]
