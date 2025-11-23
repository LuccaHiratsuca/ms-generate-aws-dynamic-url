# test_env.py
import os
from dotenv import load_dotenv
from config import AWS_REGION, BUCKET_NAME, APP_PORT

load_dotenv()

def test_environment_variables():
    print("Environment Variables Check:")
    print(f"AWS_REGION: {AWS_REGION}")
    print(f"BUCKET_NAME: {BUCKET_NAME}")
    print(f"APP_PORT: {APP_PORT}")
    
    # Check if AWS credentials are available
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    print(f"AWS_ACCESS_KEY_ID: {'***' if aws_access_key else 'NOT SET'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'***' if aws_secret_key else 'NOT SET'}")
    
    assert AWS_REGION, "AWS_REGION must be set"
    assert BUCKET_NAME, "BUCKET_NAME must be set"
    assert aws_access_key, "AWS_ACCESS_KEY_ID must be set"
    assert aws_secret_key, "AWS_SECRET_ACCESS_KEY must be set"

if __name__ == "__main__":
    test_environment_variables()