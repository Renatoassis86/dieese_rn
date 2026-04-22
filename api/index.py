from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
import os

app = FastAPI()

# Vercel Deployment Search Logic
# It looks for files in the current directory and subdirectories.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_resource(path: str):
    # Possible base locations on Vercel
    roots = [
        BASE_DIR,
        os.path.dirname(BASE_DIR), # If running from api/ folder
        os.path.join(BASE_DIR, "public"),
        os.path.join(os.path.dirname(BASE_DIR), "public")
    ]
    
    # Normalize path (remove leading slash)
    clean_path = path.lstrip("/")
    if not clean_path:
        clean_path = "index.html"

    for r in roots:
        # Check direct path
        p1 = os.path.join(r, clean_path)
        if os.path.isfile(p1):
            return p1
        # Check assets subfolder if not present
        if "assets/" not in clean_path:
            p2 = os.path.join(r, "assets", clean_path)
            if os.path.isfile(p2):
                return p2

    return None

@app.get("/{path:path}")
async def catch_all(path: str):
    f = find_resource(path)
    if f:
        return FileResponse(f)
    
    # Debug response to find where Vercel is looking
    return HTMLResponse(f"Resource not found: {path}. Server is at {BASE_DIR}. Files here: {os.listdir(BASE_DIR)}", status_code=404)
