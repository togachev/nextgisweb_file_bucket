from nextgisweb.env import _
from nextgisweb.lib.dynmenu import DynItem, Label, Link

from nextgisweb.resource import Resource, Widget
from nextgisweb.resource.view import resource_sections

from .model import FileBucket


class Widget(Widget):
    resource = FileBucket
    operation = ("create", "update")
    amdmod = "@nextgisweb/file-bucket/resource-widget"


class FileBucketMenu(DynItem):
    def build(self, args):
        yield Label("file_bucket", _("File bucket"))

        if isinstance(args.obj, FileBucket):
            if args.obj.has_export_permission(args.request.user):
                yield Link(
                    "file_bucket/export",
                    _("Export"),
                    lambda args: args.request.route_url("resource.export", id=args.obj.id),
                )


def setup_pyramid(comp, config):
    Resource.__dynmenu__.add(FileBucketMenu())

    @resource_sections(title=_("File bucket"), priority=20)
    def resource_section(obj):
        return isinstance(obj, FileBucket)
