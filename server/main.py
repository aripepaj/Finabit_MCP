#!/usr/bin/env python3
import sys

try:
    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer
    from business_data.dbConnection import get_sales_for_date, get_purchases_for_date
except ImportError:
    print("Finabit Extension: Please run 'pip install -r requirements.txt' in this folder.", file=sys.stderr)
    sys.exit(1)

import asyncio
from types import SimpleNamespace
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from business_data.dbConnection import get_sales_for_date, get_purchases_for_date

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "faq_embeddings"

notification_options = SimpleNamespace()
notification_options.tools_changed = None

EMBEDDING_MODEL = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

server = Server("faq-qdrant-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="ask",
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
            description="Returns sales (shitjet) for a specific date from the business database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date (YYYY-MM-DD)"}
                },
                "required": ["date"]
            }
        ),
        types.Tool(
            name="get_purchases",
            description="Returns purchases (blerjet) for a specific date from the business database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date (YYYY-MM-DD)"}
                },
                "required": ["date"]
            }
        ),
        types.Tool(
            name="list_faqs",
            description="Lists example FAQ questions that users can ask about Finabit's products, services, or support.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

async def get_best_faq_match(question: str):
    query_vec = EMBEDDING_MODEL.encode(question).tolist()
    hits = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        limit=1,
        with_payload=True
    )
    if hits:
        hit = hits[0]
        payload = hit.payload
        return payload.get("question"), payload.get("answer")
    else:
        return None, None

async def list_all_questions():
    scroll = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        with_payload=True,
    )
    questions = []
    for point in scroll[0]:
        payload = point.payload
        questions.append(payload.get("question", ""))
    return questions

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "ask_faq":
        question = arguments.get("question", "").strip()
        found_q, answer = await get_best_faq_match(question)
        if answer:
            reply = f"**Q:** {found_q}\n**A:** {answer}"
        else:
            qlist = await list_all_questions()
            reply = "Sorry, I could not find an answer for your question. Here are some example FAQs:\n" + "\n".join(f"- {q}" for q in qlist)
        return [types.TextContent(type="text", text=reply)]

    elif name == "list_faqs":
        qlist = await list_all_questions()
        return [types.TextContent(type="text", text="Available FAQs:\n" + "\n".join(f"- {q}" for q in qlist))]
    
    elif name == "get_sales":
        date = arguments.get("date")
        loop = asyncio.get_event_loop()
        sales = await loop.run_in_executor(None, get_sales_for_date, date)
        reply = format_sales(sales)
        return [types.TextContent(type="text", text=reply)]

    elif name == "get_purchases":
        date = arguments.get("date")
        loop = asyncio.get_event_loop()
        purchases = await loop.run_in_executor(None, get_purchases_for_date, date)
        reply = format_purchases(purchases)
        return [types.TextContent(type="text", text=reply)]

    else:
        raise ValueError(f"Unknown tool: {name}")



def format_sales(sales):
    if not sales:
        return "No sales found for that date."
    lines = ["Sales:"]
    for sale in sales:
        lines.append(f"Invoice: {sale.InvoiceNo}, Value: {sale.Value}, Partner: {sale.PartnerID}, Date: {sale.TransactionDate}")
    return "\n".join(lines)

def format_purchases(purchases):
    if not purchases:
        return "No purchases found for that date."
    lines = ["Purchases:"]
    for pur in purchases:
        lines.append(f"Invoice: {pur.InvoiceNo}, Value: {pur.Value}, Partner: {pur.PartnerID}, Date: {pur.TransactionDate}")
    return "\n".join(lines)

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