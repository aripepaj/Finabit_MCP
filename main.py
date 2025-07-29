import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastmcp import FastMCP
from dotenv import load_dotenv

# from auth.routes import router as auth_router
from app.api import sales_tool, purchases_tool, items_tool

from app.services.faq import ask_faq_api

logging.basicConfig(level=logging.INFO)

load_dotenv() 
FAQ_API_URL = os.getenv("FAQ_API_URL")

from app.main_ref import mcp

@mcp.tool(name="help", description="Ask Help system a question")
async def tool_ask_faq(question: str):
    found_q, answer = await ask_faq_api(question)
    return {"question": found_q, "answer": answer}

app = FastAPI(lifespan=mcp.http_app().lifespan)
app.mount("/mcp", mcp.http_app())

# app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/favicon.ico")
def favicon():
    return FileResponse("icon.ico")

@app.get("/manifest.json")
def get_manifest():
    return FileResponse("manifest.json", media_type="application/json")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

if __name__ == "__main__":
    mcp.run(transport="streamable-http",
            host="127.0.0.1",
            port=10000)