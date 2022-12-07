import os
from werkzeug.utils import secure_filename


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