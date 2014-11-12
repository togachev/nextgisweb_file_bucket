# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid
import os.path
from datetime import datetime
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


Base = declarative_base()


class FileBucket(Base, Resource):
    identity = 'file_bucket'
    cls_display_name = "Набор файлов"

    __scope__ = (DataStructureScope, DataScope)

    stuuid = db.Column(db.Unicode(32))
    tstamp = db.Column(db.DateTime())

    @classmethod
    def check_parent(self, parent):
        return isinstance(parent, ResourceGroup)


class FileBucketFile(Base):
    __tablename__ = 'file_bucket_file'

    file_bucket_id = db.Column(db.ForeignKey('file_bucket.id'), primary_key=True)

    name = db.Column(db.Unicode(255), primary_key=True)
    size = db.Column(db.BigInteger, nullable=False)
    mime = db.Column(db.Unicode, nullable=False)

    file_bucket = db.relationship(
        FileBucket, foreign_keys=file_bucket_id,
        backref=db.backref('files', cascade='all'))


class _files_attr(SP):

    def getter(self, srlzr):
        return map(
            lambda f: dict(name=f.name, size=f.size, mime=f.mime),
            srlzr.obj.files)

    def setter(self, srlzr, value):
        srlzr.obj.stuuid = str(uuid.uuid4().hex)
        srlzr.obj.tstamp = datetime.utcnow()

        dirname = env.file_bucket.dirname(srlzr.obj.stuuid, makedirs=True)

        for f in value:
            filedata, filemeta = env.file_upload.get_filename(f['id'])

            targetfile = os.path.abspath(os.path.join(dirname, f['name']))
            if not targetfile.startswith(dirname):
                # Проверяем на вещи типа ".." в имени файла или "/" в начале,
                # в общем в любом случае, если итоговый путь получился за
                # приделами директории в которой ожидали, то выбрасываем
                # ошибку валидации
                raise ValidationError("Insecure filename")

            copyfile(filedata, targetfile)

            fobj = FileBucketFile(
                name=f['name'], size=f['size'],
                mime=f['mime_type'])
            srlzr.obj.files.append(fobj)


class _tsamp_attr(SP):

    def getter(self, srlzr):
        if srlzr.obj.tstamp is not None:
            return srlzr.obj.tstamp.isoformat()
        else:
            return None


class FileBucketSerializer(Serializer):
    identity = FileBucket.identity
    resclass = FileBucket

    files = _files_attr(
        read=DataStructureScope.read,
        write=DataStructureScope.write)

    tstamp = _tsamp_attr(read=MetadataScope.read)
