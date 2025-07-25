# mcp_http_server.py
import json
import logging
import asyncio
from collections import deque
from typing import Dict, List, Deque, Any

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse

from mcp.server import Server
from mcp.types import Tool, TextContent

from server.tools.sales import get_sales
from server.tools.purchases import get_purchases
from server.tools.items import get_items
from server.tools.faq import ask_faq_api

# -------------------- Config --------------------
PUBLIC_BASE_URL = "https://fe8dbe856f88.ngrok-free.app"
PROTOCOL_VERSION = "2025-06-18"

INIT_RESULT_BASE: Dict[str, Any] = {
    "protocolVersion": PROTOCOL_VERSION,
    "capabilities": {
        "tools": {"list": True, "call": True},
        "logging": {"levels": ["trace", "debug", "info", "warn", "error", "fatal"]},
    },
    "serverInfo": {"name": "finabit", "version": "0.1.0"},
}

logging.basicConfig(level=logging.INFO)

# -------------------- FastAPI --------------------
app = FastAPI(title="Finabit", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# -------------------- MCP Server --------------------
mcp_server = Server("finabit-mcp")

@mcp_server.list_tools()
async def handle_list_tools() -> List[Tool]:
    return [
        Tool(
            name="get_sales",
            description="Get sales between two ISO dates (YYYY-MM-DD)",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {"type": "string", "format": "date"},
                    "to_date": {"type": "string", "format": "date"},
                },
                "required": ["from_date", "to_date"],
            },
        ),
        Tool(
            name="get_purchases",
            description="Get purchases between two ISO dates (YYYY-MM-DD)",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {"type": "string", "format": "date"},
                    "to_date": {"type": "string", "format": "date"},
                },
                "required": ["from_date", "to_date"],
            },
        ),
        Tool(
            name="get_items",
            description="Get paginated list of items",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 20},
                },
            },
        ),
        Tool(
            name="ask_faq",
            description="Ask a question to the FAQ system",
            inputSchema={
                "type": "object",
                "properties": {"question": {"type": "string"}},
                "required": ["question"],
            },
        ),
    ]

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    try:
        if name == "get_sales":
            result = get_sales(arguments["from_date"], arguments["to_date"])
        elif name == "get_purchases":
            result = get_purchases(arguments["from_date"], arguments["to_date"])
        elif name == "get_items":
            result = get_items(
                arguments.get("page_number", 1), arguments.get("page_size", 20)
            )
        elif name == "ask_faq":
            found_q, answer = await ask_faq_api(arguments["question"])
            result = {"question": found_q, "answer": answer}
        else:
            raise ValueError(f"Unknown tool: {name}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        logging.exception(f"Error in tool {name}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

# -------------------- Transport --------------------
class HTTPTransport:
    def __init__(self, server: Server):
        self.server = server

    async def handle_request(self, method: str, params: dict | None) -> dict:
        logging.info(f"[MCP] --> {method} params={params}")
        try:
            if method == "initialize":
                tools = await handle_list_tools()
                tool_list = [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": t.inputSchema,
                    }
                    for t in tools
                ]
                init = dict(INIT_RESULT_BASE)
                init["tools"] = tool_list
                init["capabilities"]["tools"]["available"] = tool_list
                logging.info(f"[MCP] <-- initialize result: {json.dumps(init)[:500]}...")
                return init

            if method == "notifications/initialized":
                logging.info("[MCP] <-- notifications/initialized acknowledged")
                return {}

            if method == "tools/list":
                tools = await handle_list_tools()
                tool_list = [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": t.inputSchema,
                    }
                    for t in tools
                ]
                logging.info(f"[MCP] <-- tools/list: {tool_list}")
                return {"tools": tool_list}

            if method == "tools/call":
                name = params.get("name")
                arguments = params.get("arguments", {})
                content = await handle_call_tool(name, arguments)
                response = {
                    "content": [{"type": c.type, "text": c.text} for c in content]
                }
                logging.info(f"[MCP] <-- tools/call result: {response}")
                return response

            raise ValueError(f"Unknown method: {method}")
        except Exception as e:
            logging.exception(f"[MCP] error in {method}")
            raise HTTPException(status_code=500, detail=str(e))

transport = HTTPTransport(mcp_server)

# -------------------- SSE --------------------
sse_clients: List[Deque[dict]] = []

async def sse_event_stream(request: Request, client_queue: Deque[dict]):
    try:
        while True:
            if await request.is_disconnected():
                break
            if client_queue:
                msg = client_queue.popleft()
                yield f"data: {json.dumps(msg)}\n\n"
            await asyncio.sleep(0.1)
    finally:
        if client_queue in sse_clients:
            sse_clients.remove(client_queue)
        logging.info("[MCP] SSE client disconnected")

def sse_broadcast(msg: dict):
    for q in sse_clients:
        q.append(msg)

@app.get("/mcp/sse")
async def mcp_sse(request: Request):
    client_queue = deque()
    sse_clients.append(client_queue)
    logging.info("[MCP] New SSE client connected")
    return StreamingResponse(sse_event_stream(request, client_queue), media_type="text/event-stream")

# -------------------- MCP HTTP --------------------
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    data = await request.json()
    method = data.get("method")
    params = data.get("params", {})
    msg_id = data.get("id")
    try:
        result = await transport.handle_request(method, params)
        response = {"jsonrpc": "2.0", "id": msg_id, "result": result}
        sse_broadcast(response)
        return response
    except Exception as e:
        err = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32000, "message": str(e)}}
        sse_broadcast(err)
        return err

@app.get("/mcp")
async def mcp_get_check():
    return {"status": "MCP", "endpoint": "/mcp"}

@app.head("/mcp")
async def mcp_head_check():
    return JSONResponse(status_code=200, content={})

@app.get("/health")
async def health():
    return {"status": "healthy"}

# -------------------- OAuth --------------------
@app.get("/.well-known/oauth-authorization-server")
async def oauth_metadata():
    return {
        "issuer": PUBLIC_BASE_URL,
        "authorization_endpoint": f"{PUBLIC_BASE_URL}/oauth/authorize",
        "token_endpoint": f"{PUBLIC_BASE_URL}/oauth/token",
        "registration_endpoint": f"{PUBLIC_BASE_URL}/oauth/register",
        "scopes_supported": ["claudeai"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "client_credentials"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
    }

@app.post("/oauth/register")
async def oauth_register(request: Request):
    data = await request.json()
    return JSONResponse({"client_id": "local-test", "client_secret": "dev-secret", "redirect_uris": data.get("redirect_uris", []), "scope": "claudeai"})

@app.get("/oauth/authorize")
async def oauth_authorize(response_type: str, client_id: str, redirect_uri: str, scope: str, state: str = ""):
    return RedirectResponse(f"{redirect_uri}?code=testcode&state={state}")

@app.post("/oauth/token")
async def oauth_token(grant_type: str = Form(...), code: str = Form(""), redirect_uri: str = Form(""), client_id: str = Form(""), client_secret: str = Form("")):
    return {"access_token": "local-token", "token_type": "bearer", "expires_in": 3600, "scope": "claudeai"}
