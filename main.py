from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.router import router
import os

app = FastAPI()
app.include_router(router, prefix="/api/v1")

app.mount("/js", StaticFiles(directory="frontend/dist/js"), name="js")
app.mount("/css", StaticFiles(directory="frontend/dist/css"), name="css")



html_path = os.path.join("frontend","dist")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(html_path, "index.html"))

@app.get("/login")
async def serve_login():
    return FileResponse(os.path.join(html_path, "login.html"))