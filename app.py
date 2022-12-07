from flask import Flask, request, redirect
from forms import MessageForm;


from werkzeug.utils import secure_filename

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

bucket = s3.list_buckets()['Buckets']

print(bucket[0]['Name'])

# curr_path = os.getcwd()
# file = 'lottery.csv'
# filename = os.path(curr_path, 'data', file)

# data = open(filename, 'rb')

# s3.upload_file(filename, bucket[0]['Name'], file)

def upload_file_to_s3(file, acl="public-read"):
    print(s3)
    filename = secure_filename(file.filename)
    s3.upload_fileobj(
        file,
        os.environ("AWS_BUCKET_NAME"),
        file.filename,
        ExtraArgs={
            "ACL": acl,
            "ContentType": file.content_type
        }
    )
    return file.filename

# pic = "\\wsl$\Ubuntu\home\ezray\rithm\exercises\week_10\sharebb\backend\computer_person.png"
####################### Routes ########################
# @app.route('/upload', methods=["GET"])
# def testCreate():

#   dataForm = {
#     'name':'test user',
#     'address': 'test address',
#     'image': "https://tinyurl.com/missing-tv",
#   }

#   upload_file_to_s3("https://tinyurl.com/missing-tv")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "user_file" not in request.files:
        return "No user_file key in request.files"
    file = request.files["user_file"]
    print(file)

    if file.filename == "":
        return "Please select a file"

    if file:
        file.filename = secure_filename(file.filename)
        output = upload_file_to_s3(file)
        return str(output)

    else:
        return redirect("/")

# @app.route("/upload", methods=["POST"])
# def testMethod():
#   print(request, "<--------- request")



# upload_file(file_name, bucket, object_name)

if __name__ == "__main__":
  app.run()