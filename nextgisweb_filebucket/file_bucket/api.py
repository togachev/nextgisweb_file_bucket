# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

import zipfile

from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import FileResponse, Response
from six import BytesIO

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

    return FileResponse(fobj.path, content_type=fobj.mime_type, request=request)


def export(resource, request):
    request.resource_permission(DataScope.read)

    data = BytesIO()
    with zipfile.ZipFile(data, mode='a', compression=zipfile.ZIP_DEFLATED, allowZip64=False) as archive:
        for f in resource.files:
            archive.write(f.path, f.name)
    data.seek(0)

    return Response(
        data.read(),
        content_type='application/zip',
        content_disposition='attachment; filename="%d.zip"' % resource.id,
    )


def setup_pyramid(comp, config):
    config.add_route(
        'file_bucket.file_download',
        r'/api/resource/{id:\d+}/file/{name:.*}',
        factory=resource_factory
    ).add_view(file_download, context=FileBucket)

    config.add_route(
        'file_bucket.export',
        r'/api/resource/{id:\d+}/file_bucket/export',
        factory=resource_factory
    ).add_view(export, context=FileBucket)
