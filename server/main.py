import asyncio
from types import SimpleNamespace
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from tools.sales import get_sales
from tools.purchases import get_purchases
from tools.faq import ask_faq_api 

notification_options = SimpleNamespace()
notification_options.tools_changed = None

server = Server("finabit")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="ask_faq",
            description="Finds and returns the best-matching FAQ answer for a user's question about Finabit. Uses semantic search for accurate retrieval.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask"
                    }
                },
                "required": ["question"]
            }
        ),
        types.Tool(
            name="get_sales",
            description="Returns sales (shitjet) for a date range from the business database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                },
                "required": ["from_date", "to_date"]
            }
        ),
        types.Tool(
            name="get_purchases",
            description="Returns purchases (blerjet) for a date range from the business database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                },
                "required": ["from_date", "to_date"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "ask":
        question = arguments.get("question", "").strip()
        found_q, answer = await ask_faq_api(question)  
        if answer:
            reply = f"**Q:** {found_q}\n**A:** {answer}"
        else:
            reply = "Sorry, I could not find an answer for your question."
        return [types.TextContent(type="text", text=reply)]
    
    elif name == "get_sales":
        from_date = arguments.get("from_date")
        to_date = arguments.get("to_date")
        reply = get_sales(from_date, to_date)
        return [types.TextContent(type="text", text=reply)]

    elif name == "get_purchases":
        from_date = arguments.get("from_date")
        to_date = arguments.get("to_date")
        reply = get_purchases(from_date, to_date)
        return [types.TextContent(type="text", text=reply)]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="Finabit",
                server_version="0.1.0",
                capabilities=server.get_capabilities(notification_options, None)
            )
        )
        
if __name__ == "__main__":
    asyncio.run(main())