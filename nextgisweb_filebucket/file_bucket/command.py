# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

import os.path
from shutil import copyfile

from nextgisweb.command import Command
from .model import FileBucketFile


@Command.registry.register
class Update_00_01Command():
    identity = 'file_bucket.update_00_01'

    @classmethod
    def argparser_setup(cls, parser, env):
        pass

    @classmethod
    def execute(cls, args, env):
        logger = env.file_bucket.logger
        logger.info("Migrate files to file storage...")
        files_moved = 0
        for fbf in FileBucketFile.filter_by(fileobj_id=None):
            dirname = env.file_bucket.dirname(fbf.file_bucket.stuuid)
            srcfile = os.path.abspath(os.path.join(dirname, fbf.name))

            fileobj = env.file_storage.fileobj(component='file_bucket')
            dstfile = env.file_storage.filename(fileobj, makedirs=True)

            copyfile(srcfile, dstfile)
            fbf.fileobj = fileobj

            files_moved += 1

        logger.info("%d files moved", files_moved)
