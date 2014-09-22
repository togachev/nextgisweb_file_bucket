# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def pkginfo():
    return dict(components=dict(
        file_bucket="nextgisweb_rekod.file_bucket"))


def amd_packages():
    return (
        ('ngw-file-bucket', 'nextgisweb_rekod:file_bucket/amd/ngw-file-bucket'),
    )
