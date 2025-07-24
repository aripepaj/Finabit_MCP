from fastapi import FastAPI
from server.tools.sales import get_sales
from server.tools.purchases import get_purchases
from server.tools.items import get_items
from server.tools.faq import ask_faq_api
from fastapi.responses import JSONResponse

app = FastAPI(title="Finabit MCP HTTP Server", version="0.1.0")

@app.post("/get_sales")
def sales_endpoint(from_date: str, to_date: str):
    return get_sales(from_date, to_date)

@app.post("/get_purchases")
def purchases_endpoint(from_date: str, to_date: str):
    return get_purchases(from_date, to_date)

@app.post("/get_items")
def items_endpoint(page_number: int = 1, page_size: int = 20):
    return get_items(page_number, page_size)

@app.post("/ask")
async def ask_endpoint(question: str):
    found_q, answer = await ask_faq_api(question)
    return {"question": found_q, "answer": answer}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.get("/.well-known/oauth-authorization-server")
async def oauth_metadata():
    return JSONResponse({
        "issuer": "http://localhost:8010",
        "authorization_endpoint": "http://localhost:8010/authorize",
        "token_endpoint": "http://localhost:8010/token",
        "registration_endpoint": "http://localhost:8010/register",
        "scopes_supported": ["test"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "client_credentials"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
    })