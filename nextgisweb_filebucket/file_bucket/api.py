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

    def zip_stream(files):
        data = BytesIO()

        def message(from_pos):
            pos = data.tell()
            data.seek(from_pos)
            return data.read(pos - from_pos)

        with zipfile.ZipFile(data, mode='a', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
            for f in files:
                pos_before = data.tell()
                archive.write(f.path, f.name)
                yield message(pos_before)

            epilogue_pos = data.tell()

        yield message(epilogue_pos)

    return Response(
        app_iter=zip_stream(resource.files),
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
