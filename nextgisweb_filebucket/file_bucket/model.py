# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid
import os
import os.path
from datetime import datetime
import dateutil
from shutil import copyfile

from nextgisweb.models import declarative_base
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
from nextgisweb.pyramid.exception import InternalServerError

from .util import _

Base = declarative_base()


class FileBucket(Base, Resource):
    identity = 'file_bucket'
    cls_display_name = _("File bucket")

    __scope__ = (DataStructureScope, DataScope)

    stuuid = db.Column(db.Unicode(32))
    tstamp = db.Column(db.DateTime())

    @classmethod
    def check_parent(self, parent):
        return isinstance(parent, ResourceGroup)
    
    @property
    def is_antique(self):
        return self.stuuid is not None


class FileBucketFile(Base):
    __tablename__ = 'file_bucket_file'

    id = db.Column(db.Integer, primary_key=True)
    file_bucket_id = db.Column(db.ForeignKey(FileBucket.id), nullable=False)
    fileobj_id = db.Column(db.ForeignKey(FileObj.id), nullable=True)
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


def find_antique_file(resource, filename):
    try:
        fobj = next(i for i in resource.files if i.name == filename)
    except StopIteration:
        return None, None

    dirname = env.file_bucket.dirname(resource.stuuid)
    path = os.path.abspath(os.path.join(dirname, fobj.name))
    return fobj, path


def validate_filename(filename):
    return not os.path.isabs(filename) and filename == os.path.normpath(filename)


class _files_attr(SP):

    def getter(self, srlzr):
        return map(
            lambda f: dict(name=f.name, size=f.size, mime_type=f.mime_type),
            srlzr.obj.files)

    def setter(self, srlzr, value):
        is_antique = srlzr.obj.is_antique
        if is_antique:
           srlzr.obj.stuuid = None

        srlzr.obj.tstamp = datetime.utcnow()

        keep = list()

        for f in value:

            if not validate_filename(f['name']):
                # Проверяем на вещи типа ".." в имени файла или "/" в начале.
                raise ValidationError("Insecure filename.")

            keep.append(f['name'])

            if 'id' in f:
                # Файл был загружен через компонент file_upload, копируем его.
                # TODO: В перспективе наверное лучше заменить на ссылки.

                fileobj = env.file_storage.fileobj(component='file_bucket')

                srcfile, metafile = env.file_upload.get_filename(f['id'])
                dstfile = env.file_storage.filename(fileobj, makedirs=True)
                copyfile(srcfile, dstfile)

                filebucketfileobj = FileBucketFile(
                    name=f['name'], size=f['size'],
                    mime_type=f['mime_type'], fileobj=fileobj)

                srlzr.obj.files.append(filebucketfileobj)

            elif is_antique:
                # Файл остался из предыдущей версии, его нужно скопировать.

                filebucketfileobj, srcfile = find_antique_file(srlzr.obj, f['name'])
                if filebucketfileobj is None:
                    raise InternalServerError('File %s lost.' % f['name'])

                fileobj = env.file_storage.fileobj(component='file_bucket')

                dstfile = env.file_storage.filename(fileobj, makedirs=True)
                copyfile(srcfile, dstfile)

                filebucketfileobj.fileobj = fileobj

        for fobj in list(srlzr.obj.files):
            if fobj.name not in keep:
                srlzr.obj.files.remove(fobj)


class _tsamp_attr(SP):

    def getter(self, srlzr):
        if srlzr.obj.tstamp is not None:
            return srlzr.obj.tstamp.isoformat()
        else:
            return None

    def setter(self, srlzr, value):
        if isinstance(value, basestring):
            srlzr.obj.tstamp = dateutil.parser.parse(value)
        elif value is None:
            srlzr.obj.tstamp = None
        else:
            raise ValidationError("Invalid timestamp value.")


class FileBucketSerializer(Serializer):
    identity = FileBucket.identity
    resclass = FileBucket

    files = _files_attr(
        read=DataStructureScope.read,
        write=DataStructureScope.write)

    tstamp = _tsamp_attr(read=MetadataScope.read, write=MetadataScope.write)
