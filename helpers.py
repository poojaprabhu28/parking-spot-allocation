import boto3
import json
import os
from datetime import datetime
import logging

#initialize logger
logging.getLogger().setLevel(logging.INFO)

# initialize s3 connection
s3_client = boto3.client('s3')

# generate timestamp for default filename
def generate_timestamp():
    return datetime.utcnow().strftime("%m%d%Y_%H%M%S")

# create json file
def store_data_to_file(upload_json_data, filename = None):
    if filename is None:
        filename = generate_timestamp()

    with open(f"{filename}.json", "w+") as f:
        f.write(json.dumps(upload_json_data, indent=1))

    return f"{filename}.json"

# upload file to s3 bucket 
def upload_to_s3_bucket(filename, bucket):
    try:
        response = s3_client.upload_file(filename, bucket, filename)
        logging.info(response)
        return "success"
    except Exception as e:
        logging.error(e)
        return "error, please check your AWS account configuration"

def delete_local_file(filename):
    try:
        os.remove(filename)
        return "success"
    except Exception as e:
        logging.error(e)
        return "error"
