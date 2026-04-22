from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Definitive fix for Vercel static file delivery:
# We mount directories and provide specific routes for root files
if os.path.exists("public"):
    app.mount("/public", StaticFiles(directory="public"), name="public")
if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/")
async def read_root():
    return FileResponse("index.html")

@app.get("/style.css")
async def read_css():
    return FileResponse("style.css")

@app.get("/api.js")
async def read_js():
    return FileResponse("api.js")

@app.get("/logo.png")
async def read_logo():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
    return HTMLResponse("Logo not found", status_code=404)

@app.get("/dashboard")
async def read_dashboard():
    return FileResponse("dashboard.html")

@app.get("/static/dashboard.html")
async def legacy_dashboard():
    return FileResponse("dashboard.html")

# Catch-all for any other static files in the root
@app.get("/{file_path:path}")
async def catch_all(file_path: str):
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return HTMLResponse("Not found", status_code=404)
