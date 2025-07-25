from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from fastapi_mcp.types import AuthConfig, MCPTool

app = FastAPI()

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

# Register tools explicitly
mcp.add_tool(
    MCPTool(
        name="echo",
        description="Echo a message back.",
        input_schema={
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"],
        },
        func=lambda args: args["message"],
    )
)

mcp.mount()
