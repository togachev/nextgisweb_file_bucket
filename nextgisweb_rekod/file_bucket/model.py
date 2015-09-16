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


class FileBucketFile(Base):
    __tablename__ = 'file_bucket_file'

    file_bucket_id = db.Column(
        db.ForeignKey('file_bucket.id'),
        primary_key=True)

    name = db.Column(db.Unicode(255), primary_key=True)
    mime_type = db.Column(db.Unicode, nullable=False)
    size = db.Column(db.BigInteger, nullable=False)

    file_bucket = db.relationship(
        FileBucket, foreign_keys=file_bucket_id,
        backref=db.backref('files', cascade='all,delete-orphan'))


class _files_attr(SP):

    def getter(self, srlzr):
        return map(
            lambda f: dict(name=f.name, size=f.size, mime_type=f.mime_type),
            srlzr.obj.files)

    def setter(self, srlzr, value):
        if srlzr.obj.stuuid is not None:
            odir = env.file_bucket.dirname(srlzr.obj.stuuid, makedirs=True)
        else:
            odir = None

        srlzr.obj.stuuid = str(uuid.uuid4().hex)
        srlzr.obj.tstamp = datetime.utcnow()

        dirname = env.file_bucket.dirname(srlzr.obj.stuuid, makedirs=True)

        keep = list()

        for f in value:
            keep.append(f['name'])
            targetfile = os.path.abspath(os.path.join(dirname, f['name']))

            if not targetfile.startswith(dirname):
                # Проверяем на вещи типа ".." в имени файла или "/" в начале,
                # в общем в любом случае, если итоговый путь получился за
                # приделами директории в которой ожидали, то выбрасываем
                # ошибку валидации.

                raise ValidationError("Insecure filename.")

            if 'id' in f:
                # Файл был загружен через компонент file_upload, копируем его.
                # TODO: В перспективе наверное лучше заменить на ссылки.

                srcfile, metafile = env.file_upload.get_filename(f['id'])
                copyfile(srcfile, targetfile)

                fobj = FileBucketFile(
                    name=f['name'], size=f['size'],
                    mime_type=f['mime_type'])

                srlzr.obj.files.append(fobj)

            else:
                # Файл остался из предыдущей версии, его нужно скопировать,
                # поскольку имя файла так же от клиента получается, его нужно
                # тоже проверять на принадлежность исходной директории.

                srcfile = os.path.abspath(os.path.join(odir, f['name']))
                if not srcfile.startswith(odir):
                    raise ValidationError("Insecure filename.")

                # Копировать долго, а ссылка должны создаваться быстро,
                # при том, что файл не изменяется это хороший вариант.

                os.link(srcfile, targetfile)

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
