from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import socket
from api.app.aws import generate_presigned_url
from api.app.config import APP_PORT


# ====================================================
# Inicialização da Aplicação
# ====================================================
app = FastAPI(debug=True)

from api.app.aws import router
app.include_router(router)

# ====================================================
# Configuração de CORS
# ====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ====================================================
# Arquivos Estáticos (HTML, CSS, JS)
# ====================================================
app.mount("/static", StaticFiles(directory="api/app/static"), name="static")


# ----------------------------------------------------
# Páginas HTML
# ----------------------------------------------------
@app.get("/home", response_class=HTMLResponse)
def home_page():
    """Página inicial da área de clientes."""
    with open("api/app/static/home.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/upload", response_class=HTMLResponse)
def upload_page():
    """Página de upload de imagens."""
    with open("api/app/static/upload.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/list", response_class=HTMLResponse)
def list_page():
    """Página de listagem de imagens."""
    with open("api/app/static/list.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/view", response_class=HTMLResponse)
def view_page():
    """Página de visualização de imagem."""
    with open("api/app/static/view.html", "r", encoding="utf-8") as f:
        return f.read()


# ====================================================
# API – Health Check (usado pelo ALB)
# ====================================================
@app.get("/health")
def health():
    hostname = socket.gethostname()
    return {
        "status": "healthy",
        "instance": hostname
    }


# ====================================================
# API – Geração de URL Pré-assinada (Upload para S3)
# ====================================================
@app.get("/generate-upload-url")
def generate_url(file_name: str, file_type: str):
    """
    Gera uma URL pré-assinada para upload direto ao S3.
    """
    url = generate_presigned_url(file_name, file_type)
    hostname = socket.gethostname()
    return {
        "upload_url": url,
        "instance": hostname
    }


# ====================================================
# Rota Raiz / Diagnóstico
# ====================================================
@app.get("/")
def root():
    """Diagnóstico simples para verificar se a API está no ar."""
    return {
        "message": "FastAPI rodando com sucesso!",
        "instance": socket.gethostname()
    }
