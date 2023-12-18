import boto3
from botocore.exceptions import NoCredentialsError
import mimetypes
import os
import pathlib
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, UploadFile, File
from fastapi import HTTPException, APIRouter, status, Depends
import io
import datetime
import hashlib
import utility.authentication_data as auth
from typing import List
from decouple import config


ACCESS_KEY_ID = config("ACCESS_KEY_ID")
SECRET_ACCESS_KEY = config("SECRET_ACCESS_KEY")
S3_BUCKET_NAME = config("S3_BUCKET_NAME")
FOLDER_BUCKET = config("FOLDER_BUCKET")

image = APIRouter(tags=["Images"], prefix="/images")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@image.post("/")
async def new(    user=Depends(auth.get_tourist_host_admin_priviledge),    file: UploadFile = File(...),):
    """
    The above function uploads a file to an AWS S3 bucket and returns the URL of the uploaded file.
    
    \n**param** user: The `user` parameter is a dependency that is obtained using the
    `auth.get_tourist_host_admin_privilege` function. It is used to authenticate and authorize the user
    making the request. The specific implementation of this function is not provided in the code
    snippet, so it is not possible to determine
    \n**param** file: The `file` parameter is of type `UploadFile` and represents the uploaded file. It is
    required and should be provided in the request
    **type** file: UploadFile
    \n**return**: a dictionary with a key "result" and the value being the URL of the uploaded image.
    """
    s3 = boto3.client(
        "s3", aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY
    )
    try:
        local_file = file.filename
        if local_file:
            extension = pathlib.Path(local_file).suffix
            new_name = hashlib.md5(
                f"{pathlib.Path(local_file).stem}_{datetime.datetime.now()}".encode()
            ).hexdigest()
            mime = mimetypes.types_map[extension]
            folder = FOLDER_BUCKET + "/" + user + "/" + new_name + extension

            file_content = await file.read()

            s3.upload_fileobj(
                io.BytesIO(file_content),
                S3_BUCKET_NAME,
                folder,
                ExtraArgs={"ACL": "public-read", "ContentType": mime},
            )

            region = s3.get_bucket_location(Bucket=S3_BUCKET_NAME)
            region = region["LocationConstraint"]
            url_image = f"https://{S3_BUCKET_NAME}.s3.{region}.amazonaws.com/{folder}"

            return {"result": url_image}
        else:
            raise HTTPException(status_code=422, detail="No input file.")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Image not found.")

    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="Not Authenticated")

    except Exception as e:
        raise (e)


@image.patch("/")
async def update(    old_file_name: str,    user=Depends(auth.get_tourist_host_admin_priviledge),    file: UploadFile = File(...),):
    """
    The `update` function uploads a file to an S3 bucket and returns the URL of the uploaded file.
    
    \n**param** old_file_name: The `old_file_name` parameter is a string that represents the name of the
    existing file that needs to be updated
    **type** old_file_name: str
    \n**param** user: The `user` parameter is used to specify the user who is updating the file. It is
    expected to be a string representing the user's name or ID. This parameter is decorated with
    `Depends(auth.get_tourist_host_admin_priviledge)`, which suggests that it is a dependency injection
    \n**param** file: The `file` parameter is of type `UploadFile` and represents the file that needs to be
    uploaded. It is required and cannot be empty
    **type** file: UploadFile
    \n**return**: a dictionary with a key "result" and the value being the URL of the uploaded image.
    """
    s3 = boto3.client(
        "s3", aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY
    )
    try:
        local_file = file.filename
        if local_file:
            extension = pathlib.Path(local_file).suffix

            mime = mimetypes.types_map[extension]
            folder = f"{FOLDER_BUCKET}/{user}/{old_file_name}"

            file_content = await file.read()

            s3.upload_fileobj(
                io.BytesIO(file_content),
                S3_BUCKET_NAME,
                folder,
                ExtraArgs={"ACL": "public-read", "ContentType": mime},
            )

            region = s3.get_bucket_location(Bucket=S3_BUCKET_NAME)
            region = region["LocationConstraint"]
            url_image = f"https://{S3_BUCKET_NAME}.s3.{region}.amazonaws.com/{folder}"

            return {"result": url_image}
        else:
            raise HTTPException(status_code=422, detail="No input file.")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Image not found.")

    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="Not Authenticated")

    except Exception as e:
        raise (e)


@image.delete("/")
async def delete(    image_name: str,    user=Depends(auth.get_tourist_host_admin_priviledge),):
    """
    The `delete` function deletes an image from an S3 bucket using the provided image name and user
    credentials.
    
    \n**param** image_name: The `image_name` parameter is a string that represents the name of the image file
    that you want to delete from the S3 bucket
    **type** image_name: str
    \n**param** user: The `user` parameter is used to specify the user who is requesting the deletion of the
    image. It is passed as an argument to the `delete` function and is expected to be a string
    representing the user's name or identifier. The `auth.get_tourist_host_admin_priviledge`
    \n**return**: a dictionary with a single key-value pair. The key is "result" and the value is a boolean
    value indicating whether the deletion was successful or not.
    """
    s3 = boto3.client(
        "s3", aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY
    )
    try:
        s3.delete_object(
            Bucket=S3_BUCKET_NAME, Key=f"{FOLDER_BUCKET}/{user}/{image_name}"
        )
        # response["ResponseMetadata"]["HTTPStatusCode"]
        return {"result": True}

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Image not found.")

    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="Not Authenticated")


@image.post("/")
async def new_list(    user=Depends(auth.get_tourist_host_admin_priviledge),    fileList: List[UploadFile] = File(...),):
    """
    The function `new_list` takes in a user and a list of files, uploads each file, and returns a list
    of URLs for the uploaded files.
    
    \n**param** user: The "user" parameter is a dependency that is obtained using the
    "auth.get_tourist_host_admin_privilege" function. It is used to authenticate and authorize the user
    making the request
    \n**param** fileList: The `fileList` parameter is a list of `UploadFile` objects. It is used to pass
    multiple files to the `new_list` function for processing
    **type** fileList: List[UploadFile]
    \n**return**: a dictionary with a key "result" and a value that is a list of URLs.
    """
    urls = []
    for file in fileList:
        urls.append((await new(file=file, user=user))["result"])
    return {"result": urls}


@image.delete("/")
async def delete_list(    fileList: List[str],    user=Depends(auth.get_tourist_host_admin_priviledge),):
    """
    The function `delete_list` takes a list of file names, deletes each file, and returns a dictionary
    with the results of the deletion.
    
    \n**param** fileList: The fileList parameter is a list of strings that represents the names of the files
    that need to be deleted
    **type** fileList: List[str]
    \n**param** user: The "user" parameter is an optional parameter that is passed to the "delete_list"
    function. It is used to authenticate the user and check if they have the necessary privileges to
    perform the delete operation
    \n**return**: a dictionary with a key "result" and the value being a list of results from deleting each
    file in the fileList.
    """
    results = []
    for file in fileList:
        results.append((await delete(image_name=file, user=user))["result"])
    return {"result": results}
