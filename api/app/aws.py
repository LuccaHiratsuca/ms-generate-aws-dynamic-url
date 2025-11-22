import boto3
from api.app.config import BUCKET_NAME, AWS_REGION

s3 = boto3.client("s3", region_name=AWS_REGION)

def generate_presigned_url(file_name: str, file_type: str):
    return s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": file_name,
            "ContentType": file_type
        },
        ExpiresIn=3600
    )
