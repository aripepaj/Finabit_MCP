# app/main_ref.py
import os, sys
from pathlib import Path
from fastmcp import FastMCP
try:
    from fastmcp.server.auth.providers.jwt import JWTVerifier as AuthProvider
except Exception:
    from fastmcp.server.auth import BearerAuthProvider as AuthProvider

def locate_public_key() -> Path:
    p = os.getenv("PUBLIC_KEY_PATH")
    if p:
        return Path(p)

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "keys" / "public.pem"

    root = Path(__file__).resolve().parents[1] 
    cand = root / "keys" / "public.pem"
    if cand.exists():
        return cand

    return Path(__file__).resolve().parent / "keys" / "public.pem"

PUBLIC_KEY_FILE = locate_public_key()
if not PUBLIC_KEY_FILE.exists():
    raise FileNotFoundError(f"public.pem not found at {PUBLIC_KEY_FILE}")

PUBLIC_KEY = PUBLIC_KEY_FILE.read_bytes()
mcp = FastMCP("Finabit", auth=AuthProvider(public_key=PUBLIC_KEY))