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
async def home_page():
    return FileResponse(os.path.join(html_path, "index.html"))

@app.get("/login")
async def login_page():
    return FileResponse(os.path.join(html_path, "login.html"))

@app.get("/dashboard")
async def dashboard_page():
    return FileResponse(os.path.join(html_path, "dashboard.html"))

@app.get("/register")
async def register_page():
    return FileResponse(os.path.join(html_path, "register.html"))


@app.get("/logout")
async def logout_link():
    return FileResponse(os.path.join(html_path, "logout.html"))


@app.get("/subjects")
async def subjects_page():
    return FileResponse(os.path.join(html_path, "subjects.html"))