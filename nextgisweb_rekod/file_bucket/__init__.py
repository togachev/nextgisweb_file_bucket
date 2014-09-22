# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path

from nextgisweb.component import Component

from .model import Base


@Component.registry.register
class FileBucketComponent(Component):
    identity = 'file_bucket'
    metadata = Base.metadata

    def setup_pyramid(self, config):
        from . import view # NOQA

    def dirname(self, stuuid, makedirs=False):
        basepath = self.settings['path']

        levels = (stuuid[0:2], stuuid[2:4], stuuid)
        path = os.path.join(basepath, *levels)

        if makedirs and not os.path.isdir(path):
            os.makedirs(path)

        return path

    settings_info = (
        dict(key='path', desc=u"Директория для хранения файлов"),
    )
