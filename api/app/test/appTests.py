# test_app.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path

# Add the parent app directory to sys.path so we can import main.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "instance" in data

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "instance" in data

@patch('main.generate_presigned_url')
def test_generate_upload_url_success(mock_generate):
    """Test successful presigned URL generation"""
    mock_url = "https://test-bucket.s3.amazonaws.com/test-file.txt?X-Amz-Expires=3600"
    mock_generate.return_value = mock_url
    
    response = client.get("/generate-upload-url?file_name=test.txt&file_type=text/plain")
    
    assert response.status_code == 200
    data = response.json()
    assert data["upload_url"] == mock_url
    assert "instance" in data
    mock_generate.assert_called_once_with("test.txt", "text/plain")

def test_generate_upload_url_missing_params():
    """Test missing query parameters"""
    response = client.get("/generate-upload-url")
    assert response.status_code == 422  # Validation error

def test_cors_headers():
    """Test CORS headers"""
    response = client.options("/")
    assert response.status_code == 200
    # FastAPI automatically handles CORS for OPTIONS requests
