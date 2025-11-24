import boto3
from fastapi import APIRouter
from api.app.config import BUCKET_NAME, AWS_REGION
import logging
import json
from fastapi import HTTPException

# Configure logging FIRST
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

s3 = boto3.client("s3", region_name=AWS_REGION)
router = APIRouter()
lambda_client = boto3.client("lambda", region_name=AWS_REGION)

def generate_presigned_url(file_name: str, file_type: str):
    return s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": f"images/{file_name}",
            "ContentType": file_type
        },
        ExpiresIn=60
    )

@router.get("/api/list-images")
def list_images():
    """Calls the Lambda READ-ALL to get the list of stored images."""
    logger.info("=== START list_images endpoint called ===")
    try:
        logger.info("Invoking Lambda function 'dynamoReadList'")
        response = lambda_client.invoke(
            FunctionName="dynamoReadList",  # Make sure this is exact
            InvocationType="RequestResponse"
        )
        logger.info("Lambda invocation successful")
    except Exception as e:
        logger.exception(f"Failed to invoke Lambda function 'dynamoReadList': {str(e)}")
        raise HTTPException(status_code=502, detail="Failed to invoke lambda function")

    status_code = response.get("StatusCode")
    function_error = response.get("FunctionError")
    logger.info(f"Lambda response - StatusCode: {status_code}, FunctionError: {function_error}")

    try:
        payload_bytes = response["Payload"].read()
        payload_text = payload_bytes.decode("utf-8") if isinstance(payload_bytes, (bytes, bytearray)) else str(payload_bytes)
        logger.debug(f"Raw payload: {payload_text}")
        payload = json.loads(payload_text)
    except Exception as e:
        logger.exception(f"Failed to read/parse payload: {str(e)}")
        payload = payload_text

    logger.info(f"Final payload: {payload}")
    logger.info("=== END list_images ===")
    return payload

@router.get("/api/get-image/{image_id}")
def get_image(image_id: str):
    """Calls the Lambda READ to get BASE64 image data."""
    logger.info(f"=== START get_image endpoint called for image_id: {image_id} ===")
    try:
        logger.info(f"Invoking Lambda function 'dynamoRead' for image id={image_id}")
        response = lambda_client.invoke(
            FunctionName="dynamoRead",
            InvocationType="RequestResponse",
            Payload=json.dumps({"imageId": image_id})
        )
        logger.info("Lambda invocation successful")
    except Exception as e:
        logger.exception(f"Failed to invoke Lambda function 'dynamoRead': {str(e)}")
        raise HTTPException(status_code=502, detail="Failed to invoke lambda function")

    status_code = response.get("StatusCode")
    function_error = response.get("FunctionError")
    logger.info(f"Lambda response - StatusCode: {status_code}, FunctionError: {function_error}")

    try:
        payload_bytes = response["Payload"].read()
        payload_text = payload_bytes.decode("utf-8") if isinstance(payload_bytes, (bytes, bytearray)) else str(payload_bytes)
        logger.debug(f"Raw payload: {payload_text}")
        payload = json.loads(payload_text)
    except Exception as e:
        logger.exception(f"Failed to read/parse payload: {str(e)}")
        payload = payload_text

    logger.info(f"Final payload: {payload}")
    logger.info("=== END get_image ===")
    return payload