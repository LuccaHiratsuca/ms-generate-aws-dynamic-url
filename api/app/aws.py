import boto3
from fastapi import APIRouter, HTTPException
from api.app.config import BUCKET_NAME, AWS_REGION
import logging
import json

# Configure logging FIRST
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

# --- DIRECT AWS CLIENTS (INSTANCE ROLE) ---
s3_client = boto3.client("s3", region_name=AWS_REGION)
lambda_client = boto3.client("lambda", region_name=AWS_REGION)


def generate_presigned_url(file_name: str, file_type: str):
    """Generate presigned URL for S3 upload (no auxiliary login needed)."""
    try:
        return s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": f"images/{file_name}",
                "ContentType": file_type
            },
            ExpiresIn=60
        )
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")


@router.get("/api/list-images")
def list_images():
    """Calls the Lambda READ-ALL to get the list of stored images."""
    logger.info("=== START list_images endpoint called ===")

    try:
        logger.info("Invoking Lambda function 'dynamoReadList'")
        response = lambda_client.invoke(
            FunctionName="dynamoReadList",
            InvocationType="RequestResponse"
        )
        logger.info("Lambda invocation successful")
    except lambda_client.exceptions.ResourceNotFoundException:
        logger.error("Lambda function 'dynamoReadList' not found")
        raise HTTPException(status_code=500, detail="Lambda function not found")
    except lambda_client.exceptions.AccessDeniedException:
        logger.error("Access denied to Lambda function 'dynamoReadList'")
        raise HTTPException(status_code=500, detail="No permission to invoke Lambda function")
    except Exception as e:
        logger.exception(f"Failed to invoke 'dynamoReadList': {str(e)}")
        raise HTTPException(status_code=502, detail="Failed to invoke lambda function")

    status_code = response.get("StatusCode")
    function_error = response.get("FunctionError")
    logger.info(f"Lambda response - StatusCode: {status_code}, FunctionError: {function_error}")

    if function_error:
        logger.error(f"Lambda function error: {function_error}")
        raise HTTPException(status_code=500, detail="Lambda function execution failed")

    try:
        payload_bytes = response["Payload"].read()
        payload_text = payload_bytes.decode("utf-8")
        payload = json.loads(payload_text)

        if isinstance(payload, dict) and payload.get("errorType"):
            logger.error(f"Lambda error: {payload}")
            raise HTTPException(status_code=500, detail=payload.get("errorMessage", "Lambda function error"))

    except json.JSONDecodeError:
        logger.exception("Failed to parse JSON payload")
        raise HTTPException(status_code=500, detail="Invalid response from Lambda function")
    except Exception as e:
        logger.exception(f"Failed to read/parse payload: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process Lambda response")

    logger.info(f"Successfully processed payload with {len(payload) if isinstance(payload, list) else 'data'}")
    logger.info("=== END list_images ===")
    return payload


@router.get("/api/get-image/{image_id}")
def get_image(image_id: str):
    """Calls the Lambda READ to get BASE64 image data."""
    logger.info(f"=== START get_image endpoint called for image_id: {image_id} ===")

    if not image_id or not image_id.strip():
        raise HTTPException(status_code=400, detail="image_id is required")

    try:
        logger.info(f"Invoking Lambda function 'dynamoRead' for image id={image_id}")
        response = lambda_client.invoke(
            FunctionName="dynamoRead",
            InvocationType="RequestResponse",
            Payload=json.dumps({"imageId": image_id})
        )
        logger.info("Lambda invocation successful")
    except lambda_client.exceptions.ResourceNotFoundException:
        logger.error("Lambda function 'dynamoRead' not found")
        raise HTTPException(status_code=500, detail="Lambda function not found")
    except lambda_client.exceptions.AccessDeniedException:
        logger.error("Access denied to Lambda function 'dynamoRead'")
        raise HTTPException(status_code=500, detail="No permission to invoke Lambda function")
    except Exception as e:
        logger.exception(f"Failed to invoke 'dynamoRead': {str(e)}")
        raise HTTPException(status_code=502, detail="Failed to invoke lambda function")

    status_code = response.get("StatusCode")
    function_error = response.get("FunctionError")
    logger.info(f"Lambda response - StatusCode: {status_code}, FunctionError: {function_error}")

    if function_error:
        logger.error(f"Lambda function error: {function_error}")
        raise HTTPException(status_code=500, detail="Lambda function execution failed")

    try:
        payload_bytes = response["Payload"].read()
        payload_text = payload_bytes.decode("utf-8")
        payload = json.loads(payload_text)

        if isinstance(payload, dict):
            if payload.get("errorType"):
                logger.error(f"Lambda error: {payload}")
                raise HTTPException(status_code=500, detail=payload.get("errorMessage", "Lambda function error"))

            if payload.get("statusCode") == 404 or payload.get("message") == "Item not found":
                logger.warning(f"Image not found: {image_id}")
                raise HTTPException(status_code=404, detail="Image not found")

    except json.JSONDecodeError:
        logger.exception("Failed to parse JSON payload")
        raise HTTPException(status_code=500, detail="Invalid response from Lambda function")
    except Exception as e:
        logger.exception(f"Failed to read/parse payload: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process Lambda response")

    logger.info(f"Successfully retrieved image data for {image_id}")
    logger.info("=== END get_image ===")
    return payload
