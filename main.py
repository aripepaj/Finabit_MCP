# main.py
import os, logging, uuid, pathlib
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

API_URL = os.getenv("API_URL", "http://localhost:5001")
PORT    = int(os.getenv("PORT", "10000"))

from app.auth import oauth
from app.main_ref import mcp
from app.tools import sales_tool, purchases_tool, items_tool, help_tool

BASE_DIR = pathlib.Path(__file__).resolve().parent
KEY_PATH = BASE_DIR / "install.key"
if not KEY_PATH.exists():
    KEY_PATH.write_text(uuid.uuid4().hex, encoding="ascii")

mcp_app = mcp.http_app(path="/")
app = FastAPI(lifespan=mcp_app.lifespan)

# static + routers
if (BASE_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(oauth.router)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finabit-mcp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/favicon.ico")
async def favicon():
    icon = BASE_DIR / "static" / "icon.ico"
    return FileResponse(str(icon)) if icon.exists() else JSONResponse({}, 200)

@app.get("/health")
def health():
    return {"status": "ok"}

app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting MCP on :{PORT} (API_URL={API_URL})")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
