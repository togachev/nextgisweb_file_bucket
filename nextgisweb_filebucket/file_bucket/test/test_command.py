# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

import os.path
from nextgisweb_filebucket.file_bucket import command
from nextgisweb_filebucket.file_bucket.model import (
    FileBucket,
    FileBucketFile
)

import webtest

TEST_FILE = {"name": "mie_phyle.txt", "content": bytes("test content")}


def test_update_00_01(env, webapp):
    webapp.authorization = ("Basic", ("administrator", "admin"))

    # Make legacy file_bucket
    data = {
        "resource": {"cls": "file_bucket", "display_name": "test-legacy-bucket", "parent": {"id": 0}},
        "file_bucket": {"files": []}
    }
    resp = webapp.post_json("/api/resource/", data)
    bucket_id = resp.json["id"]

    fb = FileBucket.filter_by(id=bucket_id).one()
    fb.stuuid = "aa" + "bb" + "legacy_bucket_dir"

    legacy_dir = env.file_bucket.dirname(fb.stuuid, makedirs=True)

    srcfile = os.path.abspath(os.path.join(legacy_dir, TEST_FILE["name"]))
    with open(srcfile, "w") as f:
        f.write(TEST_FILE["content"])

    fbf = FileBucketFile(name=TEST_FILE["name"], size=1, mime_type="no_matter")

    fb.files.append(fbf)

    # Run migrate command
    cmd = command.Update_00_01Command()
    cmd.execute(args="", env=env)

    # Check
    fb = FileBucket.filter_by(id=bucket_id).one()
    fbf = fb.files[0]
    assert fbf.fileobj

    dstfile = env.file_storage.filename(fbf.fileobj)
    with open(dstfile, "r") as f:
        assert f.read() == TEST_FILE["content"]

    webapp.delete("/api/resource/%d" % bucket_id)
