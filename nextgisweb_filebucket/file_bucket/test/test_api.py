# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

import webtest
import zipfile
import StringIO

TEST_FILE1 = {"name": "red/rose.flw", "content": bytes("rose")}
TEST_FILE2 = {"name": "orchid.flw", "content": bytes("orchid")}
TEST_FILE3 = {"name": "white/daisy.flw", "content": bytes("daisy")}


def test_bucket_crud(env, webapp):
    webapp.authorization = ("Basic", ("administrator", "admin"))

    resp = webapp.post("/api/component/file_upload/upload", [
        ["files[]", webtest.Upload(TEST_FILE1["name"], TEST_FILE1["content"])],
        ["files[]", webtest.Upload(TEST_FILE2["name"], TEST_FILE2["content"])],
        ["files[]", webtest.Upload(TEST_FILE3["name"], TEST_FILE3["content"])]
    ])

    data = {
        "resource": {"cls": "file_bucket", "display_name": "test-bucket", "parent": {"id": 0}},
        "file_bucket": {"files": resp.json["upload_meta"]}
    }
    resp = webapp.post_json("/api/resource/", data, status=201)
    bucket_id = resp.json["id"]

    resp = webapp.get("/resource/%d/file/%s" % (bucket_id, TEST_FILE1["name"]), status=200)
    assert resp.body == TEST_FILE1["content"]
    resp = webapp.get("/resource/%d/file/%s" % (bucket_id, TEST_FILE2["name"]), status=200)
    assert resp.body == TEST_FILE2["content"]
    resp = webapp.get("/resource/%d/file/%s" % (bucket_id, TEST_FILE3["name"]), status=200)
    assert resp.body == TEST_FILE3["content"]

    webapp.put_json("/api/resource/%d" % bucket_id, {
       "file_bucket": {"files": [{"name": "iam/../bad"}]}
    }, status=422)

    resp = webapp.put_json("/api/resource/%d" % bucket_id, {
        "file_bucket": {"files": [{"name": TEST_FILE1["name"]}]}
    }, status=200)
    webapp.get("/resource/%d/file/%s" % (bucket_id, TEST_FILE1["name"]), status=200)
    webapp.get("/resource/%d/file/%s" % (bucket_id, TEST_FILE2["name"]), status=404)

    webapp.delete("/api/resource/%d" % bucket_id, status=200)
    webapp.get("/resource/%d/file/%s" % (bucket_id, TEST_FILE3["name"]), status=404)

def test_create_from_archive(env, webapp):
    webapp.authorization = ("Basic", ("administrator", "admin"))

    data = StringIO.StringIO()
    archive = zipfile.ZipFile(data, "a", zipfile.ZIP_DEFLATED, False)
    archive.writestr(TEST_FILE1["name"], TEST_FILE1["content"])
    archive.writestr(TEST_FILE2["name"], TEST_FILE2["content"])
    archive.close()
    data.seek(0)

    resp = webapp.put("/api/component/file_upload/upload", data.read())
    archive_id = resp.json["id"]

    bucket_data = {
        "resource": {"cls": "file_bucket", "display_name": "test-bucket-from-archive", "parent": {"id": 0}},
        "file_bucket": {"archive": {"id": archive_id}, "files": []}
    }
    webapp.post_json("/api/resource/", bucket_data, status=422)

    del bucket_data["file_bucket"]["files"]
    resp = webapp.post_json("/api/resource/", bucket_data, status=201)
    bucket_id = resp.json["id"]

    resp = webapp.get("/resource/%d/file/%s" % (bucket_id, TEST_FILE1["name"]), status=200)
    assert resp.body == TEST_FILE1["content"]
    resp = webapp.get("/resource/%d/file/%s" % (bucket_id, TEST_FILE2["name"]), status=200)
    assert resp.body == TEST_FILE2["content"]

    webapp.delete("/api/resource/%d" % bucket_id, status=200)
