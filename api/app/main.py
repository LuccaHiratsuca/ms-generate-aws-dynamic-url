from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

import socket

from api.app.aws import generate_presigned_url
from api.app.config import APP_PORT

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
# Servindo arquivos estáticos (HTML)
# ----------------------------------------------------
app.mount("/static", StaticFiles(directory="api/app/static"), name="static")

@app.get("/upload", response_class=HTMLResponse)
def upload_page():
    """
    Página simples de upload.
    """
    with open("api/app/static/upload.html", "r", encoding="utf-8") as f:
        return f.read()

# ----------------------------------------------------
# HEALTH CHECK (ALB)
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
    """
    Recebe nome e tipo do arquivo e devolve URL pré-assinada.
    """
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
