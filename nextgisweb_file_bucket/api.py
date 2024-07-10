import zipstream
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from nextgisweb.pyramid.tomb import UnsafeFileResponse
from nextgisweb.resource import Resource, DataScope, resource_factory, DataStructureScope, ResourceScope
from nextgisweb.pyramid import viewargs

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from nextgisweb.postgis.exception import ExternalDatabaseError
from nextgisweb.env import _, DBSession

from .model import FileBucket, FileBucketFile, FileResource

PERM_UPDATE = ResourceScope.update
PERM_READ = ResourceScope.read

def file_download(resource, request):
    request.resource_permission(DataScope.read)

    fname = request.matchdict["name"]
    fobj = FileBucketFile.filter_by(file_bucket_id=resource.id, name=fname).one_or_none()
    if fobj is None:
        raise HTTPNotFound()

    return UnsafeFileResponse(fobj.path, content_type=fobj.mime_type, request=request)


def export(resource, request):
    request.resource_permission(DataScope.read)

    zip_stream = zipstream.ZipFile(mode="w", compression=zipstream.ZIP_DEFLATED, allowZip64=True)
    for f in resource.files:
        zip_stream.write(f.path, arcname=f.name)

    return Response(
        app_iter=zip_stream,
        content_type="application/zip",
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
                link = request.route_url('resource.file_download', id=fbf.file_bucket_id, name=fbf.name),
                res_name = res.display_name,
            ))
        status = len(result) > 0 if True else False
    except KeyError:
        result=None
        status=False

    return dict(
        result=result,
        status=status)

@viewargs(renderer='json')
def file_resource_all(request):
    result = list()
    try:
        query = DBSession.query(Resource, FileResource, FileBucketFile) \
            .join(FileResource, FileResource.id == Resource.id) \
            .join(FileBucketFile, FileBucketFile.id == FileResource.file_resource_id) \
            .filter(FileResource.id == Resource.id)

        for resource, file_resource, file_bucket_file in query:
            if resource.has_permission(PERM_READ, request.user):
                result.append(dict(
                    key = str(resource.id) + ":" + str(file_resource.file_resource_id),
                    resource_id = resource.id,
                    resource_name = resource.display_name,
                    cls = resource.cls,
                    file_resource_id = file_resource.file_resource_id,
                    file_bucket_id = file_bucket_file.file_bucket_id,
                    fileobj_id = file_bucket_file.fileobj_id,
                    name=file_bucket_file.name,
                    mime_type = file_bucket_file.mime_type,
                    size = file_bucket_file.size,
                    link = request.route_url('resource.file_download', id=file_bucket_file.file_bucket_id, name=file_bucket_file.name),
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
        file_download,
        route_name="resource.file_download",
        context=FileBucket,
        request_method='GET',
    )

    config.add_view(
        export,
        route_name="resource.export",
        context=FileBucket,
        request_method='GET',
    )

    config.add_route(
        'file_bucket.export',
        r'/api/resource/{id:uint}/file_bucket/export',
        factory=resource_factory,
        request_method="GET",
        get=export,
    )

    config.add_route(
        'file_resource.create',
        r'/api/file-resource/{id:uint}/create/{fid:uint}/',
        factory=resource_factory,
        get=file_resource_create
    )

    config.add_route(
        'file_resource.delete',
        r'/api/file-resource/{id:uint}/delete/{fid:uint}/',
        factory=resource_factory,
        get=file_resource_delete
    )

    config.add_route(
        'file_resource.delete_all',
        r'/api/file-resource/{id:uint}/delete_all',
        factory=resource_factory,
        get=file_resource_delete_all
    )

    config.add_route(
        'file_resource.show',
        '/api/file-resource/{id:uint}/show',
        factory=resource_factory,
        get=file_resource_show
    )

    config.add_route(
        'file_resource.all',
        '/api/file-resource/all',
        get=file_resource_all
    )