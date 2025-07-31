from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider

with open("keys/public.pem", "rb") as f:
    PUBLIC_KEY = f.read()

mcp = FastMCP("Finabit", auth=BearerAuthProvider(public_key=PUBLIC_KEY))