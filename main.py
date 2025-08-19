# main.py
import os, sys, logging, uuid
from pathlib import Path
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

import importlib.metadata
try:
    import fastmcp  
    try:
        _ = importlib.metadata.version("fastmcp")
    except importlib.metadata.PackageNotFoundError:
        import types
        if not hasattr(fastmcp, "__version__"):
            fastmcp.__version__ = "0.0.0"
except Exception:
    pass


try:
    from dotenv import load_dotenv  # add `python-dotenv` to requirements.txt
    load_dotenv()                   # reads .env in the working directory
except Exception:
    pass


def resource_path(*parts: str) -> Path:
    """
    Path to bundled, read-only resources.
    In onefile builds, this points inside the PyInstaller temp (_MEIPASS).
    In dev, it points to the folder containing this file.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent
    return base.joinpath(*parts)

def appdata_path(*parts: str) -> Path:
    """
    Persistent, user-writable path (e.g., %APPDATA%/FinabitMCP on Windows).
    Use for files you create/write at runtime (like install.key).
    """
    appdata_root = os.getenv("APPDATA")
    if appdata_root:
        root = Path(appdata_root)
    else:
        root = Path.home() / ".finabitmcp"
    d = root / "FinabitMCP"
    d.mkdir(parents=True, exist_ok=True)
    return d.joinpath(*parts)

API_URL = os.getenv("API_URL", "http://localhost:5001")
PORT    = int(os.getenv("PORT", "10000"))
SSL_CERTFILE = os.getenv("SSL_CERTFILE")  # optional
SSL_KEYFILE  = os.getenv("SSL_KEYFILE")   # optional

from app.auth import oauth
from app.main_ref import mcp
from app.tools import sales_tool, purchases_tool, items_tool, help_tool

BASE_DIR = resource_path()

KEY_PATH = appdata_path("install.key")
if not KEY_PATH.exists():
    KEY_PATH.write_text(uuid.uuid4().hex, encoding="ascii")

mcp_app = mcp.http_app(path="/")
app = FastAPI(lifespan=mcp_app.lifespan)

static_dir = resource_path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

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
    icon = resource_path("static", "icon.ico")
    return FileResponse(str(icon)) if icon.exists() else JSONResponse({}, 200)

@app.get("/health")
def health():
    return {"status": "ok"}

app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting MCP on :{PORT} (API_URL={API_URL})")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        ssl_certfile=SSL_CERTFILE,
        ssl_keyfile=SSL_KEYFILE,
        proxy_headers=True,
        forwarded_allow_ips="*")
