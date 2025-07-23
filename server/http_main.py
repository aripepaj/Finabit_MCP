from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict, Any

from .tools.sales import get_sales
from .tools.purchases import get_purchases
from .tools.items import get_items
from .tools.faq import ask_faq_api

app = FastAPI(
    title="Finabit MCP HTTP Server",
    version="0.1.0"
)

# MCP /list_tools endpoint
@app.get("/list_tools")
async def list_tools():
    return [
        {
            "name": "ask",
            "description": "Find and return the best-matching FAQ answer for a user's question about Finabit.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask"
                    }
                },
                "required": ["question"]
            }
        },
        {
            "name": "get_sales",
            "description": "Returns sales (shitjet) for a date range.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                },
                "required": ["from_date", "to_date"]
            }
        },
        {
            "name": "get_purchases",
            "description": "Returns purchases (blerjet) for a date range.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                },
                "required": ["from_date", "to_date"]
            }
        },
        {
            "name": "get_items",
            "description": "Returns items (artikujt) from the inventory/catalog with pagination support.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "description": "Page number (default: 1)"},
                    "page_size": {"type": "integer", "description": "Items per page (default: 20)"}
                },
                "required": []
            }
        }
    ]

# MCP /call_tool endpoint
class CallToolBody(BaseModel):
    name: str
    arguments: Dict[str, Any]

# @app.post("/list_tools")
# async def call_tool(body: CallToolBody):
#     name = body.name
#     arguments = body.arguments

#     if name == "ask":
#         question = arguments.get("question", "").strip()
#         found_q, answer = await ask_faq_api(question)
#         if answer:
#             reply = f"**Q:** {found_q}\n**A:** {answer}"
#         else:
#             reply = "Sorry, I could not find an answer for your question."
#         return {"content": reply}

#     elif name == "get_sales":
#         from_date = arguments.get("from_date")
#         to_date = arguments.get("to_date")
#         sales = get_sales(from_date, to_date)
#         return {"content": sales}

#     elif name == "get_purchases":
#         from_date = arguments.get("from_date")
#         to_date = arguments.get("to_date")
#         purchases = get_purchases(from_date, to_date)
#         return {"content": purchases}

#     elif name == "get_items":
#         page_number = arguments.get("page_number", 1)
#         page_size = arguments.get("page_size", 20)
#         items = get_items(page_number, page_size)
#         return {"content": items}

#     else:
#         return {"error": f"Unknown tool: {name}"}
    
@app.post("/call_tool")
async def call_tool(body: CallToolBody):
    return {"content": f"Ran tool {body.name} with arguments {body.arguments}"}

# Optionally, you can add a health check
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}