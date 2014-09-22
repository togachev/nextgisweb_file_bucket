# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nextgisweb.resource import Widget
from .model import FileBucket


class Widget(Widget):
    resource = FileBucket
    operation = ('create', 'update')
    amdmod = 'ngw-file-bucket/Widget'
