import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BUCKET_NAME = os.getenv("BUCKET_NAME", "site-institucional-grupo-e")
APP_PORT = int(os.getenv("APP_PORT", 8000))