from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from api.app.aws import generate_presigned_url
from api.app.config import APP_PORT
import socket

app = FastAPI()

# ----------------------------------------------------
# CORS
# ----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ----------------------------------------------------
# HEALTH CHECK (para o ALB)
# ----------------------------------------------------
@app.get("/health")
def health():
    hostname = socket.gethostname()
    return {
        "status": "healthy",
        "instance": hostname
    }

# ----------------------------------------------------
# ROTA PARA URL PRÉ-ASSINADA
# ----------------------------------------------------
@app.get("/generate-upload-url")
def generate_url(file_name: str, file_type: str):
    url = generate_presigned_url(file_name, file_type)
    hostname = socket.gethostname()
    return {
        "upload_url": url,
        "instance": hostname
    }


# ----------------------------------------------------
# ROOT
# ----------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "FastAPI rodando com sucesso!",
        "instance": socket.gethostname()
    }
