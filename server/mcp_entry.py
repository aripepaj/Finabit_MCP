# mcp_http_server.py
import asyncio
import json
import logging
from typing import Any, Dict, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
import httpx

from server.tools.sales import get_sales
from server.tools.purchases import get_purchases
from server.tools.items import get_items
from server.tools.faq import ask_faq_api

# Create MCP server
mcp_server = Server("finabit-mcp")

@mcp_server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_sales",
            description="Get sales between two ISO dates (YYYY-MM-DD)",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {"type": "string", "format": "date"},
                    "to_date": {"type": "string", "format": "date"}
                },
                "required": ["from_date", "to_date"]
            }
        ),
        Tool(
            name="get_purchases",
            description="Get purchases between two ISO dates (YYYY-MM-DD)",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {"type": "string", "format": "date"},
                    "to_date": {"type": "string", "format": "date"}
                },
                "required": ["from_date", "to_date"]
            }
        ),
        Tool(
            name="get_items",
            description="Get paginated list of items",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 20}
                }
            }
        ),
        Tool(
            name="ask_faq",
            description="Ask a question to the FAQ system",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string"}
                },
                "required": ["question"]
            }
        )
    ]

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "get_sales":
            result = get_sales(arguments["from_date"], arguments["to_date"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_purchases":
            result = get_purchases(arguments["from_date"], arguments["to_date"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_items":
            result = get_items(
                arguments.get("page_number", 1),
                arguments.get("page_size", 20)
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "ask_faq":
            found_q, answer = await ask_faq_api(arguments["question"])
            result = {"question": found_q, "answer": answer}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logging.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

# Create FastAPI app for HTTP transport
app = FastAPI(title="Finabit MCP Server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://claude.ai", "https://*.anthropic.com"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

class HTTPTransport:
    """HTTP transport for MCP server"""
    
    def __init__(self, server: Server):
        self.server = server
        self.session = None
    
    async def initialize_session(self):
        if not self.session:
            # Create a mock transport for the MCP server
            read_stream = MockReadStream()
            write_stream = MockWriteStream()
            
            # Initialize the server
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="finabit-mcp",
                    server_version="0.1.0"
                )
            )
    
    async def handle_request(self, method: str, params: dict = None) -> dict:
        """Handle MCP protocol requests"""
        try:
            if method == "initialize":
                return {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "logging": {}
                    },
                    "serverInfo": {
                        "name": "finabit-mcp",
                        "version": "0.1.0"
                    }
                }
            
            elif method == "tools/list":
                tools = await handle_list_tools()
                return {
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema
                        }
                        for tool in tools
                    ]
                }
            
            elif method == "tools/call":
                name = params.get("name")
                arguments = params.get("arguments", {})
                content = await handle_call_tool(name, arguments)
                return {
                    "content": [
                        {"type": item.type, "text": item.text}
                        for item in content
                    ]
                }
            
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class MockReadStream:
    async def read(self) -> bytes:
        return b""

class MockWriteStream:
    async def write(self, data: bytes):
        pass

# Initialize transport
transport = HTTPTransport(mcp_server)

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Main MCP protocol endpoint"""
    try:
        data = await request.json()
        method = data.get("method")
        params = data.get("params", {})
        msg_id = data.get("id")
        
        result = await transport.handle_request(method, params)
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result
        }
        
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": data.get("id") if 'data' in locals() else None,
            "error": {
                "code": -32000,
                "message": str(e)
            }
        }

@app.get("/health")
async def health():
    return {"status": "healthy"}