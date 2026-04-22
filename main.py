from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Definitive Catch-all for Vercel Static Serving
@app.get("/{path:path}")
async def catch_all(path: str):
    # Try current directory
    local_path = os.path.join(BASE_DIR, path if path else "index.html")
    if os.path.isfile(local_path):
        return FileResponse(local_path)
    
    # Try public folder
    public_path = os.path.join(BASE_DIR, "public", path)
    if os.path.isfile(public_path):
        return FileResponse(public_path)

    # Try assets folder
    assets_path = os.path.join(BASE_DIR, "assets", path)
    if os.path.isfile(assets_path):
        return FileResponse(assets_path)

    # Handle root /
    if not path:
        return FileResponse(os.path.join(BASE_DIR, "index.html"))

    return HTMLResponse(f"File not found: {path}", status_code=404)
