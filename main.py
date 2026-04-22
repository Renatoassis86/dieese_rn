from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

# Mount static files correctly
# Vercel handles static files automatically if they are in public/ or at root
# But for local dev, we keep this.
if os.path.exists("public"):
    app.mount("/public", StaticFiles(directory="public"), name="public")
if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")

templates = Jinja2Templates(directory=".")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    if os.path.exists("dashboard.html"):
        return templates.TemplateResponse("dashboard.html", {"request": request})
    return HTMLResponse("Dashboard file not found", status_code=404)

# REMOVED /logo.png custom route to let Vercel serve it as a static file
# This prevents Error 500 issues on the server side.
