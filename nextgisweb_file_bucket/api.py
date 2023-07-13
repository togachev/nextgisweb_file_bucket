import zipstream
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import FileResponse, Response

from nextgisweb.pyramid import viewargs
from nextgisweb.resource import Resource, DataScope, resource_factory, DataStructureScope, ResourceScope

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from nextgisweb.postgis.exception import ExternalDatabaseError
from nextgisweb.resource.exception import ResourceError
from nextgisweb.env import _, DBSession

from .model import FileBucket, FileBucketFile, FileResource

PERM_UPDATE = ResourceScope.update
PERM_READ = ResourceScope.read

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

    zip_stream = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED, allowZip64=True)
    for f in resource.files:
        zip_stream.write(f.path, arcname=f.name)

    return Response(
        app_iter=zip_stream,
        content_type='application/zip',
        content_disposition='attachment; filename="%d.zip"' % resource.id,
    )
@viewargs(renderer='json')
def file_resource_create(request):
    request.resource_permission(PERM_UPDATE)
    fid = int(request.matchdict['fid'])
    try:
        query = FileResource(id=request.context.id, file_resource_id=fid)
        DBSession.add(query)   
        DBSession.flush()
    except SQLAlchemyError as exc:
        raise ExternalDatabaseError(message=_("ERROR: duplicate key violates unique constraint."), sa_error=exc)

    return dict(id=request.context.id, file_resource_id=fid)

@viewargs(renderer='json')
def file_resource_delete(request):
    request.resource_permission(PERM_UPDATE)
    obj = FileResource.filter_by(id=request.context.id,
        file_resource_id=int(request.matchdict['fid'])).one()
    DBSession.delete(obj)
    DBSession.flush()
    return None

@viewargs(renderer='json')
def file_resource_delete_all(request):
    request.resource_permission(PERM_UPDATE)
    DBSession.query(FileResource).filter_by(id=request.context.id).delete()
    DBSession.flush()
    return None

@viewargs(renderer='json')
def file_resource_show(resource, request):
    request.resource_permission(PERM_READ)
    result = list()
    try:
        query = DBSession.query(FileResource, FileBucketFile, Resource) \
            .join(FileBucketFile, FileResource.file_resource_id == FileBucketFile.id) \
            .join(Resource, FileBucketFile.file_bucket_id == Resource.id) \
            .filter(FileResource.id == resource.id)
        for fr, fbf, res in query:
            result.append(dict(
                resource_id = fr.id,
                file_resource_id = fr.file_resource_id,
                id = fbf.id,
                file_bucket_id = fbf.file_bucket_id,
                fileobj_id = fbf.fileobj_id,
                name=fbf.name,
                mime_type = fbf.mime_type,
                size = fbf.size,
                link = request.route_url('file_bucket.file_download', id=fbf.file_bucket_id, name=fbf.name),
                res_name = res.display_name,
            ))
        status = len(result) > 0 if True else False
    except KeyError:
        result=None
        status=False

    return dict(
        result=result,
        status=status)

def setup_pyramid(comp, config):
    config.add_view(
        file_download, route_name='resource.file_download', context=FileBucket)
    config.add_route(
        'file_bucket.file_download',
        r'/api/resource/{id:\d+}/file_bucket/file/{name:.*}',
        factory=resource_factory
    ).add_view(file_download, context=FileBucket)

    config.add_view(export, route_name='resource.export', context=FileBucket)
    config.add_route(
        'file_bucket.export',
        r'/api/resource/{id:\d+}/file_bucket/export',
        factory=resource_factory
    ).add_view(export, context=FileBucket)

    config.add_route(
        'file_resource.create',
        r'/api/file-resource/{id:\d+}/create/{fid:\d+}/',
        factory=resource_factory
    ).add_view(
        file_resource_create
    )

    config.add_route(
        'file_resource.delete',
        r'/api/file-resource/{id:\d+}/delete/{fid:\d+}/',
        factory=resource_factory
    ).add_view(
        file_resource_delete
    )

    config.add_route(
        'file_resource.delete_all',
        r'/api/file-resource/{id:\d+}/delete_all',
        factory=resource_factory
    ).add_view(
        file_resource_delete_all
    )

    config.add_route(
        'file_resource.show',
        r'/api/file-resource/{id:\d+}/show',
        factory=resource_factory,
        client=('id',)
    ).add_view(file_resource_show)