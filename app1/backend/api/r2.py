import boto3
import json
import os



client = boto3.client('s3',
    endpoint_url = f'https://2c24417b72a01185d3e997b637987dfa.r2.cloudflarestorage.com',
    aws_access_key_id = "d257b3fe7d75d9c534d8c5f44f275666",
    aws_secret_access_key = "7392d58cd8ebcf0ed7d119902cd853938558ee5b357a3796815c5bb15faa6227",
    config=boto3.session.Config(signature_version='s3v4',)
    )


def upload(file_name):

    # file_name = "reviews.csv"

    response= client.upload_file(file_name,"klh",file_name)
    return response

def get_presigned_url(file_name):
    res = client.generate_presigned_url('get_object',
                                        Params={'Bucket': "klh",
                                                            'Key': file_name},
                                                    ExpiresIn=3600)
    return res
