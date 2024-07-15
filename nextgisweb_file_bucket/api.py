import zipstream
from itertools import groupby
from operator import itemgetter
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from nextgisweb.pyramid.tomb import UnsafeFileResponse
from nextgisweb.resource import Resource, DataScope, resource_factory, DataStructureScope, ResourceScope
from nextgisweb.pyramid import viewargs

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from nextgisweb.postgis.exception import ExternalDatabaseError
from nextgisweb.env import _, DBSession

from nextgisweb.core.exception import ForbiddenError, InsufficientPermissions

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
def file_resource_group_show(resource, request):
    result = list()
    query = DBSession.query(FileResource, FileBucketFile, Resource) \
        .join(FileBucketFile, FileResource.file_resource_id == FileBucketFile.id) \
        .join(Resource, FileBucketFile.file_bucket_id == Resource.id) \
        .filter(FileResource.id == resource.id)
    
    for fr, fbf, res in query:
        if res.has_permission(PERM_READ, request.user):
            result.append(dict(
                resource_id = fr.id,
                file_resource_id = fr.file_resource_id,
                id = fbf.id,
                key = fbf.id,
                file_bucket_id = fbf.file_bucket_id,
                fileobj_id = fbf.fileobj_id,
                name=fbf.name,
                mime_type = fbf.mime_type,
                size = fbf.size,
                link = request.route_url('resource.file_download', id=fbf.file_bucket_id, name=fbf.name),
                res_name = res.display_name,
            ))

    res = dict()
    for item in result:
        res[item["res_name"]] = res.get(item["res_name"], [])
        res[item["res_name"]].append(item)

    return res

@viewargs(renderer='json')
def file_resource_show(resource, request):
    result = list()
    query = DBSession.query(FileResource, FileBucketFile, Resource) \
        .join(FileBucketFile, FileResource.file_resource_id == FileBucketFile.id) \
        .join(Resource, FileBucketFile.file_bucket_id == Resource.id) \
        .filter(FileResource.id == resource.id)
    
    for fr, fbf, res in query:
        if res.has_permission(PERM_READ, request.user):
            result.append(dict(
                resource_id = fr.id,
                file_resource_id = fr.file_resource_id,
                id = fbf.id,
                key = fbf.id,
                file_bucket_id = fbf.file_bucket_id,
                fileobj_id = fbf.fileobj_id,
                name=fbf.name,
                mime_type = fbf.mime_type,
                size = fbf.size,
                link = request.route_url('resource.file_download', id=fbf.file_bucket_id, name=fbf.name),
                res_name = res.display_name,
            ))
    return result

@viewargs(renderer='json')
def files(request):
    result = list()
    query = DBSession.query(FileBucketFile, FileBucket) \
        .join(FileBucketFile, FileBucket.id == FileBucketFile.file_bucket_id)

    for fbf, fb in query:
        if fb.has_permission(PERM_READ, request.user):
            result.append(dict(
                file_bucket_id = fbf.file_bucket_id,
                fileobj_id = fbf.fileobj_id,
                name=fbf.name,
                mime_type = fbf.mime_type,
                size = fbf.size,
                link = request.route_url('resource.file_download', id=fbf.file_bucket_id, name=fbf.name),
                file_bucket_name = fb.display_name,
            ))

    return result

@viewargs(renderer='json')
def file_resource(resource, request):
    if resource.cls in ['mapserver_style', 'qgis_vector_style', 'qgis_raster_style', 'wmsclient_layer', 'tmsclient_layer']:
        if resource.has_permission(PERM_UPDATE, request.user):
            fileList = list() # список всех файлов
            fileItem = list() # список файлов ресурса

            query = DBSession.query(FileBucketFile, Resource) \
                .join(Resource, FileBucketFile.file_bucket_id == Resource.id)
            for fbf, res in query:
                fileList.append(dict(
                    id = fbf.id,
                    file_bucket_id = fbf.file_bucket_id,
                    fileobj_id = fbf.fileobj_id,
                    name=fbf.name,
                    mime_type = fbf.mime_type,
                    size = fbf.size,
                    res_name = res.display_name,
                ))

            fres = DBSession.query(FileResource).filter(FileResource.id == request.context.id)
            for fr in fres:
                fileItem.append(dict(
                    id = fr.file_resource_id,
                ))
            return dict(
                props=dict(id=request.context.id, fileList=fileList, fileItem=fileItem)
            )
        else:
            raise InsufficientPermissions()
    else:
        raise ForbiddenError()

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
        'file_resource.data',
        r'/file-resource/{id:uint}/data',
        factory=resource_factory,
        get=file_resource
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
        'file_resource.group_show',
        '/api/file-resource/{id:uint}/group_show',
        factory=resource_factory,
        get=file_resource_group_show
    )

    config.add_route(
        'file_resource.all',
        '/api/file-resource/all',
        get=files
    )