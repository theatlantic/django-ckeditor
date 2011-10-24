from django.conf.urls.defaults import patterns, url
import os

urlpatterns = patterns(
    '',
    url(r'^upload/', 'ckeditor.views.upload', name='ckeditor_upload'),
    url(r'^browse/', 'ckeditor.views.browse', name='ckeditor_browse'),
    url(r"^media/(?P<path>.*)$", "django.views.static.serve", {"document_root": os.path.dirname(__file__) + "/media/ckeditor/ckeditor"}, "ckeditor_static"),
)
