from uuid import uuid4
import boto
import os.path
from flask import current_app as app
from werkzeug.utils import secure_filename
import flask


def s3_upload(source_file, upload_dir=None, bucket=None, acl='public-read'):
    """ Uploads WTForm File Object to Amazon S3

        Expects following app.config attributes to be set:
            S3_KEY              :   S3 API Key
            S3_SECRET           :   S3 Secret Key
            S3_BUCKET           :   What bucket to upload to
            S3_UPLOAD_DIRECTORY :   Which S3 Directory.

        The default sets the access rights on the uploaded file to
        public-read.  It also generates a unique filename via
        the uuid4 function combined with the file extension from
        the source file.
    """

    details = {}
    details['success'] = False
    details['url'] = ""
    details['etag'] = ""
    details['name'] = ""


    if not source_file.data.filename:
        return details

    if bucket is None:
        bucket = app.config["S3_BUCKET"]
    if upload_dir is None:
        upload_dir = app.config["S3_UPLOAD_DIRECTORY"]

    source_filename = secure_filename(source_file.data.filename)
    source_extension = os.path.splitext(source_filename)[1]

    destination_filename = uuid4().hex + source_extension

    # Connect to S3 and upload file.
    conn = boto.connect_s3(
        app.config["S3_KEY"],
        app.config["S3_SECRET"],
        host=app.config['S3_LOCATION']
    )
    b = conn.get_bucket(bucket)

    key = "/".join([upload_dir, destination_filename])
    sml = b.new_key(key)
    sml.set_contents_from_string(source_file.data.read())
    sml.set_acl(acl)

    details['success'] = True
    details['url'] = sml.generate_url(expires_in=0, query_auth=False)
    details['etag'] = sml.key
    details['name'] = source_filename
    details['key'] = key
    details['bucket'] = app.config["S3_BUCKET"]

    return details


def static_proxy(path, bucket=None):
    if not bucket:
        bucket = app.config["S3_BUCKET"]
    conn = boto.connect_s3(
        app.config["S3_KEY"],
        app.config["S3_SECRET"],
        host=app.config['S3_LOCATION']
    )
    b = conn.get_bucket(bucket)
    key = boto.s3.key.Key(b)
    key.key = path

    try:
        key.open_read()
        headers = dict(key.resp.getheaders())
        return flask.Response(key, headers=headers)
    except boto.exception.S3ResponseError as e:
        return flask.Response(e.body, status=e.status, headers=key.resp.getheaders())
