from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Mount static files for local development
if os.path.exists("public"):
    app.mount("/public", StaticFiles(directory="public"), name="public")
if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/", response_class=FileResponse)
async def read_root():
    # Direct file response is more stable on Vercel than Jinja2 for basic static sites
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("index.html not found", status_code=404)

@app.get("/dashboard", response_class=FileResponse)
async def read_dashboard():
    if os.path.exists("dashboard.html"):
        return FileResponse("dashboard.html")
    return HTMLResponse("Dashboard file not found", status_code=404)

# Keep the static dashboard link for compatibility
@app.get("/static/dashboard.html", response_class=FileResponse)
async def legacy_dashboard():
    return await read_dashboard()
