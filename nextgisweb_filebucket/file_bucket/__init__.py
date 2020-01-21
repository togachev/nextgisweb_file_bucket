# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals
import os.path
from shutil import copyfileobj

from nextgisweb.component import Component

from .model import Base, FileBucket
from . import command

class FileBucketComponent(Component):
    identity = 'file_bucket'
    metadata = Base.metadata

    def initialize(self):
        self.path = self.settings.get('path') or self.env.core.gtsdir(self)

    def initialize_db(self):
        if 'path' not in self.settings:
            self.env.core.mksdir(self)

    def setup_pyramid(self, config):
        from . import api, view  # NOQA
        api.setup_pyramid(self, config)
        view.setup_pyramid(self, config)

    def dirname(self, stuuid, makedirs=False):
        levels = (stuuid[0:2], stuuid[2:4], stuuid)
        path = os.path.join(self.path, *levels)

        if makedirs and not os.path.isdir(path):
            os.makedirs(path)

        return path

    settings_info = (
        dict(key='path', desc=u"Директория для хранения файлов"),
    )
