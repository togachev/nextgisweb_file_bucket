from nextgisweb.env import gettext
from nextgisweb.lib.dynmenu import Label, Link

from nextgisweb.jsrealm import jsentry
from nextgisweb.resource import Resource, Widget
from nextgisweb.resource.view import resource_sections

from .model import FileBucket


class FileBucketWidget(Widget):
    resource = FileBucket
    operation = ("create", "update")
    amdmod = jsentry("@nextgisweb/file-bucket/resource-widget")


@resource_sections("@nextgisweb/file-bucket/resource-section")
def resource_section(obj, **kwargs):
    return isinstance(obj, FileBucket)


def setup_pyramid(comp, config):
    @Resource.__dynmenu__.add
    def _resource_dynmenu(args):
        yield Label("file_bucket", gettext("File bucket"))

        if isinstance(args.obj, FileBucket):
            if args.obj.has_export_permission(args.request.user):
                yield Link(
                    "file_bucket/export",
                    label=gettext("Export"),
                    url=lambda args: args.request.route_url("resource.export", id=args.obj.id),
                )
