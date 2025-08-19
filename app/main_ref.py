from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider

def bundle_path(*parts: str) -> Path:
    """Resolve data file both in dev and in PyInstaller onefile builds."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent
    return base.joinpath(*parts)

PUBLIC_KEY_FILE = bundle_path("keys", "public.pem")
PUBLIC_KEY = PUBLIC_KEY_FILE.read_bytes()

mcp = FastMCP("Finabit", auth=BearerAuthProvider(public_key=PUBLIC_KEY))