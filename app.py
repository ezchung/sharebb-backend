from flask import Flask, request, redirect, url_for, flash, render_template
from util.helpers import upload_file_to_s3, s3

from werkzeug.utils import secure_filename

# Regular flask way,

import os
import sys
import boto3

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
BUCKET_NAME = os.environ["AWS_BUCKET_NAME"]

# IPython and try out to see if works
# Method to list buckets, see if authenticating

# bucket = s3.list_buckets()['Buckets']

# print(bucket[0]['Name'])

# curr_path = os.getcwd()
# file = 'lottery.csv'
# filename = os.path(curr_path, 'data', file)

# data = open(filename, 'rb')

# s3.upload_file(filename, bucket[0]['Name'], file)

# def upload_file_to_s3(file, acl="public-read"):
#     print(s3)
#     filename = secure_filename(file.filename)
#     s3.upload_fileobj(
#         file,
#         os.environ("AWS_BUCKET_NAME"),
#         file.filename,
#         ExtraArgs={
#             "ACL": acl,
#             "ContentType": file.content_type
#         }
#     )
#     return file.filename

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

@app.route("/")
def render_form():
    return render_template("form.html")

# function to check file extension
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def create():
    # breakpoint()
    # check whether an input field with name 'user_file' exist
    if 'user_file' not in request.files:
        flash('No user_file key in request.files')
        return redirect(url_for('new'))

    # after confirm 'user_file' exist, get the file from input
    file = request.files['user_file']

    # check whether a file is selected
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('new'))

    # check whether the file extension is allowed (eg. png,jpeg,jpg,gif)
    if file and allowed_file(file.filename):
        output = upload_file_to_s3(file)

        # if upload success,will return file name of uploaded file
        if output:
            # write your code here
            # to save the file name in database
            sThree = boto3.client('s3')
            print(output, "<----- output")
            print(sThree, BUCKET_NAME, "<--------- sthree bucket")
            result = s3.list_buckets()
            print(result, "<----- result")
            flash("Success upload")
            return redirect("/")

        # upload failed, redirect to upload page
        else:
            flash("Unable to upload, try again")
            return redirect(url_for('new'))

    # if file extension not allowed
    else:
        flash("File type not accepted,please try again.")
        return redirect(url_for('new'))

if __name__ == "__main__":
  app.run()