# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

import os.path

from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import FileResponse

from nextgisweb.env import env
from nextgisweb.resource import DataScope, resource_factory

from .model import FileBucket, FileBucketFile


def file_download(resource, request):
    request.resource_permission(DataScope.read)

    fname = request.matchdict["name"]
    fobj = FileBucketFile.filter_by(
        file_bucket_id=resource.id,
        name=fname
    ).one_or_none()
    if fobj is None:
        raise HTTPNotFound()

    if fobj.is_antique:
        dirname = env.file_bucket.dirname(resource.stuuid)
        path = os.path.abspath(os.path.join(dirname, fobj.name))
    else:
        path = env.file_storage.filename(fobj.fileobj)

    return FileResponse(path, content_type=fobj.mime_type, request=request)


def setup_pyramid(comp, config):
    config.add_route(
        'file_bucket.file_download',
        r'/api/resource/{id}/file/{name:.*}',
        factory=resource_factory
    ).add_view(file_download, context=FileBucket)
