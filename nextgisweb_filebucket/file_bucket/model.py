import os
import os.path
from datetime import datetime
import dateutil
from shutil import copyfile, copyfileobj
import zipfile
import magic

from nextgisweb.models import DBSession, declarative_base
from nextgisweb import db
from nextgisweb.resource import (
    Resource,
    Serializer,
    SerializedProperty as SP,
    DataStructureScope,
    DataScope,
    MetadataScope,
    ValidationError,
    ResourceGroup)
from nextgisweb.env import env
from nextgisweb.file_storage import FileObj

from .util import _

Base = declarative_base()


class FileBucket(Base, Resource):
    identity = 'file_bucket'
    cls_display_name = _("File bucket")

    __scope__ = (DataStructureScope, DataScope)

    tstamp = db.Column(db.DateTime())

    @classmethod
    def check_parent(self, parent):
        return isinstance(parent, ResourceGroup)


class FileBucketFile(Base):
    __tablename__ = 'file_bucket_file'

    id = db.Column(db.Integer, primary_key=True)
    file_bucket_id = db.Column(db.ForeignKey(FileBucket.id), nullable=False)
    fileobj_id = db.Column(db.ForeignKey(FileObj.id), nullable=False)
    name = db.Column(db.Unicode(255), nullable=False)
    mime_type = db.Column(db.Unicode, nullable=False)
    size = db.Column(db.BigInteger, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(file_bucket_id, name),
    )

    fileobj = db.relationship(FileObj, lazy='joined')

    file_bucket = db.relationship(
        FileBucket, foreign_keys=file_bucket_id,
        backref=db.backref('files', cascade='all,delete-orphan'))

    @property
    def path(self):
        return env.file_storage.filename(self.fileobj)


def validate_filename(filename):
    # Проверяем на вещи типа ".." в имени файла или "/" в начале.
    return not os.path.isabs(filename) and filename == os.path.normpath(filename)


class _archive_attr(SP):

    def setter(self, srlzr, value):
        archive_name, metafile = env.file_upload.get_filename(value['id'])

        old_files = list(srlzr.obj.files)

        with DBSession.no_autoflush:
            for f in old_files:
                srlzr.obj.files.remove(f)

        DBSession.flush()

        with zipfile.ZipFile(archive_name, mode='r', allowZip64=True) as archive:

            for file_info in archive.infolist():

                if file_info.is_dir():
                    continue

                if not validate_filename(file_info.filename):
                    raise ValidationError(message="Insecure filename.")

                fileobj = env.file_storage.fileobj(component='file_bucket')

                dstfile = env.file_storage.filename(fileobj, makedirs=True)
                with archive.open(file_info.filename, 'r') as sf, open(dstfile, 'w+b') as df:
                    copyfileobj(sf, df)
                    df.seek(0)
                    mime_type = magic.from_buffer(df.read(1024), mime=True)

                filebucketfileobj = FileBucketFile(
                    name=file_info.filename, size=file_info.file_size,
                    mime_type=mime_type, fileobj=fileobj)

                srlzr.obj.files.append(filebucketfileobj)


class _files_attr(SP):

    def getter(self, srlzr):
        return [dict(name=f.name, size=f.size, mime_type=f.mime_type)
            for f in srlzr.obj.files]

    def setter(self, srlzr, value):
        srlzr.obj.tstamp = datetime.utcnow()

        files_info = dict()
        for f in value:
            name = f.pop('name')
            if not validate_filename(name):
                raise ValidationError(message="Insecure filename.")
            files_info[name] = f

        removed_files = list()
        for filebucket_file in srlzr.obj.files:
            if filebucket_file.name not in files_info:  # Removed file
                removed_files.append(filebucket_file)
            else:
                file_info = files_info.pop(filebucket_file.name)
                if 'id' in file_info:  # Updated file
                    srcfile, metafile = env.file_upload.get_filename(file_info['id'])
                    dstfile = env.file_storage.filename(filebucket_file.fileobj, makedirs=False)
                    copyfile(srcfile, dstfile)
                else:  # Untouched file
                    pass

        for f in removed_files:
            srlzr.obj.files.remove(f)

        for name, file_info in files_info.items():  # New file
            fileobj = env.file_storage.fileobj(component='file_bucket')

            srcfile, metafile = env.file_upload.get_filename(file_info['id'])
            dstfile = env.file_storage.filename(fileobj, makedirs=True)
            copyfile(srcfile, dstfile)

            filebucket_file = FileBucketFile(
                name=name, size=file_info['size'],
                mime_type=file_info['mime_type'], fileobj=fileobj)

            srlzr.obj.files.append(filebucket_file)


class _tsamp_attr(SP):

    def getter(self, srlzr):
        if srlzr.obj.tstamp is not None:
            return srlzr.obj.tstamp.isoformat()
        else:
            return None

    def setter(self, srlzr, value):
        if isinstance(value, str):
            srlzr.obj.tstamp = dateutil.parser.parse(value)
        elif value is None:
            srlzr.obj.tstamp = None
        else:
            raise ValidationError(message="Invalid timestamp value.")


class FileBucketSerializer(Serializer):
    identity = FileBucket.identity
    resclass = FileBucket

    archive = _archive_attr(
        read=None,
        write=DataStructureScope.write)

    files = _files_attr(
        read=DataStructureScope.read,
        write=DataStructureScope.write)

    tstamp = _tsamp_attr(read=MetadataScope.read, write=MetadataScope.write)

    def deserialize(self):
        if 'files' in self.data and 'archive' in self.data:
            raise ValidationError(message="'files' and 'archive' attributes should not pass together.")
        super().deserialize()
