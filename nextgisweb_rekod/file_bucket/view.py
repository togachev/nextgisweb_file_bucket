# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path

from pyramid.response import FileResponse
from pyramid.httpexceptions import HTTPNotFound

from nextgisweb.resource import Resource, Widget, resource_factory, DataScope
from nextgisweb.env import env
from .model import FileBucket


class Widget(Widget):
    resource = FileBucket
    operation = ('create', 'update')
    amdmod = 'ngw-file-bucket/Widget'


def file_download(resource, request):
    request.resource_permission(DataScope.read)

    try:
        fname = request.matchdict['name']
        fobj = next(i for i in resource.files if i.name == fname)
    except StopIteration:
        raise HTTPNotFound()

    dirname = env.file_bucket.dirname(resource.stuuid)
    path = os.path.abspath(os.path.join(dirname, fobj.name))

    return FileResponse(path, request=request)


def setup_pyramid(comp, config):
    config.add_route(
        'file_bucket.file_download',
        '/resource/{id}/file/{name}',
        factory=resource_factory
    ).add_view(file_download, context=FileBucket)

    Resource.__psection__.register(
        key='file_bucket', priority=20, title="Набор файлов",
        is_applicable=lambda obj: isinstance(obj, FileBucket),
        template='nextgisweb_rekod:file_bucket/template/section.mako')
