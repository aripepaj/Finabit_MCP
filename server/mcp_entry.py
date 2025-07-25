from server.main import app  # <--- Import THE SAME app with routes!
from fastapi_mcp import FastApiMCP
from fastapi_mcp.types import AuthConfig

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
mcp.mount()
