import boto3, botocore
import os
from werkzeug.utils import secure_filename

s3 = boto3.client(
  "s3",
  "us-west-1",
  aws_access_key_id=os.getenv('aws_access_key_id'),
  aws_secret_access_key=os.getenv('aws_secret_access_key'),
)

def upload_file_to_s3(file, acl="public-read"):
    filename = secure_filename(file.filename)
    s3.upload_fileobj(
        file,
        os.getenv("AWS_BUCKET_NAME"),
        file.filename,
        ExtraArgs={
            "ACL": acl,
            "ContentType": file.content_type
        }
    )
    return file.filename