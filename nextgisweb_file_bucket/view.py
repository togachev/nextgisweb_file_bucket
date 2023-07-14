
from nextgisweb.env import _, DBSession
from nextgisweb.lib.dynmenu import DynItem, Label, Link

from nextgisweb.pyramid import viewargs

from nextgisweb.resource import Resource, Widget, resource_factory, ResourceScope
from nextgisweb.resource.view import resource_sections
from nextgisweb.core.exception import ForbiddenError

from .model import FileBucket, FileResource, FileBucketFile

PERM_UPDATE = ResourceScope.update

class Widget(Widget):
    resource = FileBucket
    operation = ('create', 'update')
    amdmod = 'ngw-file-bucket/Widget'


class FileBucketMenu(DynItem):
    def build(self, args):
        yield Label('file_bucket', _('File bucket'))

        if isinstance(args.obj, FileBucket):
            if args.obj.has_export_permission(args.request.user):
                yield Link(
                    'file_bucket/export', _('Export'),
                    lambda args: args.request.route_url('resource.export', id=args.obj.id),
                )

@viewargs(renderer='react')
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
                entrypoint='@nextgisweb/file_bucket/file-resource',
                props=dict(id=request.context.id, fileList=fileList, fileItem=fileItem),
                obj=request.context,
                title=_("Files"))
        else:
            raise InsufficientPermissions()
    else:
        raise ForbiddenError()

def setup_pyramid(comp, config):
    config.add_route(
        'file_resource.settings',
        r'/file-resource/{id:\d+}/settings',
        factory=resource_factory,
        client=('id',)
    ).add_view(file_resource)

    Resource.__dynmenu__.add(FileBucketMenu())

    @resource_sections(title=_("File bucket"), priority=20)
    def resource_section(obj):
        return isinstance(obj, FileBucket)
