# test_integration.py
import requests
import json
from config import APP_PORT

def test_full_workflow():
    """Test the complete workflow (requires running app and valid AWS credentials)"""
    base_url = f"http://localhost:{APP_PORT}"
    
    # Test health endpoint
    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200
    print("Health check: ✓")
    
    # Test presigned URL generation
    params = {
        "file_name": "test-integration-file.txt",
        "file_type": "text/plain"
    }
    
    url_response = requests.get(f"{base_url}/generate-upload-url", params=params)
    assert url_response.status_code == 200
    
    data = url_response.json()
    presigned_url = data["upload_url"]
    
    print(f"Generated presigned URL: {presigned_url}")
    
    # Test uploading a file (optional - requires valid presigned URL)
    if presigned_url and presigned_url.startswith("https://"):
        try:
            test_content = b"This is a test file content"
            upload_response = requests.put(
                presigned_url,
                data=test_content,
                headers={"Content-Type": "text/plain"}
            )
            print(f"Upload test completed with status: {upload_response.status_code}")
        except Exception as e:
            print(f"Upload test failed (this might be expected): {e}")
    
    print("Integration test completed!")

if __name__ == "__main__":
    test_full_workflow()