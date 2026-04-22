from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
import os

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_file(path: str):
    """
    Highly resilient file finder that searches across all potential locations.
    Handles 'assets/...' and 'public/...' paths by checking direct and subfolder matches.
    """
    if not path:
        return None
        
    search_paths = [
        os.path.join(BASE_DIR, path),
        os.path.join(BASE_DIR, "src", "app", path),
        os.path.join(BASE_DIR, "public", path),
        os.path.join(BASE_DIR, "assets", path),
        # Fallback for when path already contains assets/ or public/
        os.path.join(BASE_DIR, path.replace("assets/", "").replace("public/", "")),
    ]
    
    for p in search_paths:
        if os.path.isfile(p):
            return p
    return None

@app.get("/")
async def read_root():
    f = find_file("index.html")
    if f: return FileResponse(f)
    return HTMLResponse("index.html not found", status_code=404)

@app.get("/{path:path}")
async def catch_all(path: str):
    if not path:
        return await read_root()
        
    f = find_file(path)
    if f:
        return FileResponse(f)
        
    return HTMLResponse(f"File not found: {path}", status_code=404)
