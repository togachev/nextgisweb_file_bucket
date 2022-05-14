import os.path
from shutil import copyfile
import transaction

from nextgisweb.lib.logging import logger
from nextgisweb.command import Command
from .model import FileBucketFile, FileBucket


@Command.registry.register
class MigrateFileStorageCommand():
    identity = 'file_bucket.migrate_file_storage'

    @classmethod
    def argparser_setup(cls, parser, env):
        pass

    @classmethod
    def execute(cls, args, env):
        logger.info("Migrate files to file storage...")

        files_moved = fb_count = 0
        with transaction.manager:
            for fbf in FileBucketFile.filter_by(fileobj_id=None):
                dirname = env.file_bucket.dirname(fbf.file_bucket.stuuid)
                srcfile = os.path.abspath(os.path.join(dirname, fbf.name))

                fileobj = env.file_storage.fileobj(component='file_bucket')
                dstfile = env.file_storage.filename(fileobj, makedirs=True)

                copyfile(srcfile, dstfile)
                fbf.fileobj = fileobj

                files_moved += 1

            for fb in FileBucket.query().filter(FileBucket.stuuid != None):
                fb.stuuid = None
                fb_count += 1

        logger.info("%d files moved from %d file buckets", files_moved, fb_count)
