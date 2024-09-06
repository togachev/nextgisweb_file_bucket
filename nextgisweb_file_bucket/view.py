from nextgisweb.env import gettext, DBSession
from nextgisweb.lib.dynmenu import DynItem, Label, Link

from nextgisweb.pyramid import viewargs

from nextgisweb.resource import Resource, Widget, resource_factory, ResourceScope
from nextgisweb.resource.view import resource_sections
from nextgisweb.core.exception import ForbiddenError, InsufficientPermissions

from .model import FileBucket, FileResource, FileBucketFile



class Widget(Widget):
    resource = FileBucket
    operation = ("create", "update")
    amdmod = "@nextgisweb/file-bucket/resource-widget"


class FileBucketMenu(DynItem):
    def build(self, args):
        yield Label("file_bucket", gettext("File bucket"))

        if isinstance(args.obj, FileBucket):
            if args.obj.has_export_permission(args.request.user):
                yield Link(
                    "file_bucket/export",
                    gettext("Export"),
                    lambda args: args.request.route_url("resource.export", id=args.obj.id),
                )

@viewargs(renderer='react')
def file_resource(resource, request):
    if resource.cls in ['mapserver_style', 'qgis_vector_style', 'qgis_raster_style', 'wmsclient_layer', 'tmsclient_layer']:
        if resource.has_permission(ResourceScope.update, request.user):
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
                entrypoint='@nextgisweb/file-bucket/file-resource',
                props=dict(id=request.context.id, fileList=fileList, fileItem=fileItem),
                obj=request.context,
                title=gettext("Files"))
        else:
            raise InsufficientPermissions()
    else:
        raise ForbiddenError()

def setup_pyramid(comp, config):
    config.add_route(
        'file_resource.settings',
        r'/file-resource/{id:uint}/settings',
        factory=resource_factory,
    ).add_view(file_resource)

    Resource.__dynmenu__.add(FileBucketMenu())

    @resource_sections(title=gettext("File bucket"), priority=20)
    def resource_section(obj):
        return isinstance(obj, FileBucket)
