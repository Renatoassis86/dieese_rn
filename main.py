from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Observatório Rural RN")

# Montar diretório de arquivos estáticos (CSS, JS, Imagens)
# O caminho é relativo à localização do main.py
static_dir = os.path.join(os.path.dirname(__file__), "src", "app")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    # Retorna o dashboard principal
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "DASHBOARD NÃO ENCONTRADO. Verifique src/app/index.html"}

@app.get("/api/health")
async def health_check():
    return {"status": "online", "project": "Observatório Rural RN"}

# Para rodar localmente: uvicorn main:app --reload
