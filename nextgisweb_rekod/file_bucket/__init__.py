# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path
from shutil import copyfileobj

from nextgisweb.component import Component
from nextgisweb.core import BackupBase

from .model import Base, FileBucket


@BackupBase.registry.register
class FileBucketFileBackup(BackupBase):
    identity = 'file_bucket_file'

    def is_binary(self):
        return True

    def backup(self):
        stuuid, name = self.key.split(':', 1)
        dirname = self.comp.dirname(stuuid)
        fname = os.path.join(dirname, name)
        with open(fname, 'rb') as fd:
            copyfileobj(fd, self.binfd)

    def restore(self):
        stuuid, name = self.key.split(':', 1)
        dirname = self.comp.dirname(stuuid, makedirs=True)
        fname = os.path.join(dirname, name)
        with open(fname, 'wb') as fd:
            copyfileobj(self.binfd, fd)


@Component.registry.register
class FileBucketComponent(Component):
    identity = 'file_bucket'
    metadata = Base.metadata

    def initialize(self):
        self.path = self.settings.get('path') or self.env.core.gtsdir(self)

    def initialize_db(self):
        if 'path' not in self.settings:
            self.env.core.mksdir(self)

    def setup_pyramid(self, config):
        from . import view  # NOQA
        view.setup_pyramid(self, config)

    def dirname(self, stuuid, makedirs=False):
        levels = (stuuid[0:2], stuuid[2:4], stuuid)
        path = os.path.join(self.path, *levels)

        if makedirs and not os.path.isdir(path):
            os.makedirs(path)

        return path

    def backup(self):
        for i in super(FileBucketComponent, self).backup():
            yield i

        for file_bucket in FileBucket.query():
            for f in file_bucket.files:
                yield FileBucketFileBackup(
                    self, file_bucket.stuuid + ':' + f.name)

    settings_info = (
        dict(key='path', desc=u"Директория для хранения файлов"),
    )
