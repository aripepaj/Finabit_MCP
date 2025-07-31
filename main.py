import os
import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.auth import oauth
from app.main_ref import mcp
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

SECRET_KEY = os.environ.get("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

from app.api import sales_tool, purchases_tool, items_tool, help_tool

mcp_app = mcp.http_app(path="/")
app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(oauth.router)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://claude.ai", "https://*.anthropic.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/icon.ico")


app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting OAuth MCP Server for Claude...")
    uvicorn.run(app, host="0.0.0.0", port=10000)