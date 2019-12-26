# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path

from pyramid.response import FileResponse
from pyramid.httpexceptions import HTTPNotFound

from nextgisweb.resource import Resource, Widget, resource_factory, DataScope
from nextgisweb.env import env
from .model import FileBucket, FileBucketFile, find_antique_file

from .util import _

class Widget(Widget):
    resource = FileBucket
    operation = ('create', 'update')
    amdmod = 'ngw-file-bucket/Widget'


def file_download(resource, request):
    request.resource_permission(DataScope.read)

    if resource.is_antique:
        path = find_antique_file(resource, request.matchdict['name'])[1]
        if path is None:
            raise HTTPNotFound()
    else:
        fobj = FileBucketFile.filter_by(
            file_bucket_id=request.matchdict["id"],
            name=request.matchdict["name"]
        ).one_or_none()
        if fobj is None:
            raise HTTPNotFound()
        path = env.file_storage.filename(fobj.fileobj)

    return FileResponse(path, content_type=bytes(fobj.mime_type), request=request)


def setup_pyramid(comp, config):
    config.add_route(
        'file_bucket.file_download',
        r'/resource/{id}/file/{name:.*}',
        factory=resource_factory
    ).add_view(file_download, context=FileBucket)

    Resource.__psection__.register(
        key='file_bucket', priority=20, title=_("File bucket"),
        is_applicable=lambda obj: isinstance(obj, FileBucket),
        template='nextgisweb_filebucket:file_bucket/template/section.mako')
