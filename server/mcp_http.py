import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastmcp import FastMCP

from tools.sales import get_sales
from tools.purchases import get_purchases
from tools.items import get_items
from tools.faq import ask_faq_api 

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("Finabit", stateless_http=True)

@mcp.tool(name="get_sales", description="Get sales between two ISO dates")
def tool_get_sales(from_date: str, to_date: str):
    return get_sales(from_date, to_date)

@mcp.tool(name="get_purchases", description="Get purchases between two ISO dates")
def tool_get_purchases(from_date: str, to_date: str):
    return get_purchases(from_date, to_date)

@mcp.tool(name="get_items", description="Get paginated list of items")
def tool_get_items(page_number: int = 1, page_size: int = 20):
    return get_items(page_number, page_size)

@mcp.tool(name="help", description="Ask Help system a question")
async def tool_ask_faq(question: str):
    found_q, answer = await ask_faq_api(question)
    return {"question": found_q, "answer": answer}

app = FastAPI(lifespan=mcp.http_app().lifespan)
app.mount("/mcp", mcp.http_app())

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    mcp.run(transport="streamable-http",
            host="127.0.0.1",
            port=10000)
