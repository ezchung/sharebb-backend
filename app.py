from flask import Flask

import os
import sys
import boto3
app = Flask(__name__)

s3 = boto3.client(
  "s3", # Needs to be S digit 3
  "us-west-1",
  aws_access_key_id=os.environ['aws_access_key_id'],
  aws_secret_access_key=os.environ['aws_secret_access_key'],
)
# IPython and try out to see if works
# Method to list buckets, see if authenticating
buckets = s3.list_buckets()['Buckets']

print(buckets)

# upload_file(file_name, bucket, object_name)

if __name__ == "__main__":
  app.run()