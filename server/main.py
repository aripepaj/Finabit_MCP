from fastapi import FastAPI
from server.tools.sales import get_sales
from server.tools.purchases import get_purchases
from server.tools.items import get_items
from server.tools.faq import ask_faq_api
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi import Form
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter()

app = FastAPI(title="Finabit MCP HTTP Server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.post("/mcp/list_tools")
async def list_tools():
    return {
        "tools": [
            {
                "name": "get_sales",
                "description": "Get sales data between two dates.",
                "parameters": [
                    {"name": "from_date", "type": "string", "description": "Start date YYYY-MM-DD"},
                    {"name": "to_date", "type": "string", "description": "End date YYYY-MM-DD"},
                ]
            },
            {
                "name": "get_purchases",
                "description": "Get purchase data between two dates.",
                "parameters": [
                    {"name": "from_date", "type": "string"},
                    {"name": "to_date", "type": "string"},
                ]
            },
        ]
    }

@app.post("/mcp/call_tool")
async def call_tool(request: Request):
    data = await request.json()
    tool = data.get("tool")
    parameters = data.get("parameters", {})
    if tool == "get_sales":
        return {"result": get_sales(parameters["from_date"], parameters["to_date"])}
    elif tool == "get_purchases":
        return {"result": get_purchases(parameters["from_date"], parameters["to_date"])}
    else:
        return {"error": "Unknown tool"}
    

@app.get("/.well-known/oauth-authorization-server")
async def oauth_metadata():
    return JSONResponse({
        "issuer": "https://finabit-mcp.onrender.com",
        "authorization_endpoint": "https://finabit-mcp.onrender.com/oauth/authorize",
        "token_endpoint": "https://finabit-mcp.onrender.com/oauth/token",
        "registration_endpoint": "https://finabit-mcp.onrender.com/oauth/register",
        "scopes_supported": ["claudeai", "test"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "client_credentials"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
    })

@router.post("/oauth/register")
async def oauth_register(request: Request):
    data = await request.json()
    return JSONResponse({
        "client_id": "local-test",
        "client_secret": "dev-secret",
        "redirect_uris": data.get("redirect_uris", []),
        "scope": "claudeai"
    })

@router.get("/oauth/authorize")
async def oauth_authorize(response_type: str, client_id: str, redirect_uri: str, scope: str, state: str = ""):
    code = "testcode"
    return RedirectResponse(f"{redirect_uri}?code={code}&state={state}")

@router.post("/oauth/token")
async def oauth_token(
    grant_type: str = Form(...),
    code: str = Form(""),
    redirect_uri: str = Form(""),
    client_id: str = Form(""),
    client_secret: str = Form("")
):
    return {
        "access_token": "local-token",
        "token_type": "bearer",
        "expires_in": 3600,
        "scope": "claudeai"
    }

app.include_router(router)