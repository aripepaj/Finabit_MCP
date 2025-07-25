from fastapi import FastAPI
from fastapi_mcp import FastApiMCP, tool
from fastapi_mcp.types import AuthConfig
from server.tools.sales import get_sales

app = FastAPI(title="Finabit MCP HTTP Server", version="0.1.0")

# OAuth setup, CORS, and other routes (healthz, ask, etc.) remain as-is.

# Initialize FastApiMCP
mcp = FastApiMCP(
    app,
    auth_config=AuthConfig(
        version="2025-03-26",
        client_id="local-test",
        client_secret="dev-secret",
        issuer="https://finabit-mcp.onrender.com",
        default_scope="claudeai",
        setup_proxies=False,
        setup_fake_dynamic_registration=True,
    )
)

@tool(name="echo", description="Echo a message back.")
def echo_tool(message: str):
    return message

@tool(name="get_sales", description="Return sales between two ISO dates (YYYY-MM-DD).")
def get_sales_tool(from_date: str, to_date: str):
    return get_sales(from_date, to_date)

# Mount MCP routes
mcp.mount()
