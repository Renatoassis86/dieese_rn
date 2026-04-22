from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Precise static mapping for Vercel
# This ensures that even if CWD changes, Vercel finds the assets
assets_path = os.path.join(BASE_DIR, "assets")
public_path = os.path.join(BASE_DIR, "public")

if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
if os.path.exists(public_path):
    app.mount("/public", StaticFiles(directory=public_path), name="public")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/style.css")
async def read_css():
    return FileResponse(os.path.join(BASE_DIR, "style.css"))

@app.get("/api.js")
async def read_js():
    return FileResponse(os.path.join(BASE_DIR, "api.js"))

@app.get("/logo.png")
async def read_logo():
    # Try multiple locations for the logo to ensure visibility
    paths = [
        os.path.join(BASE_DIR, "logo.png"),
        os.path.join(public_path, "logo.png"),
        os.path.join(BASE_DIR, "src", "app", "logo.png")
    ]
    for p in paths:
        if os.path.exists(p):
            return FileResponse(p)
    return HTMLResponse("Logo not found", status_code=404)

@app.get("/dashboard")
async def read_dashboard():
    return FileResponse(os.path.join(BASE_DIR, "dashboard.html"))

# Comprehensive catch-all with absolute path resolution
@app.get("/{file_path:path}")
async def catch_all(file_path: str):
    full_path = os.path.join(BASE_DIR, file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(full_path)
    
    # Fallback to src/app if file_path is relative to root
    src_path = os.path.join(BASE_DIR, "src", "app", file_path)
    if os.path.exists(src_path) and os.path.isfile(src_path):
        return FileResponse(src_path)
        
    return HTMLResponse(f"Not found: {file_path}", status_code=404)
