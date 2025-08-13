import os
import secrets
import logging
from datetime import datetime, timedelta
import hashlib
import base64
from typing import Optional

from fastapi import HTTPException, Header

from app.core.db import get_db_connection
from app.core.keys import PRIVATE_KEY, PUBLIC_KEY
from jose import jwt
from app.auth.state import oauth_sessions, registered_clients

HERE = os.path.dirname(os.path.abspath(__file__))
INSTALL_KEY_PATH = os.path.join(HERE, "..", "..", "install.key")

INSTALL_KEY = os.environ.get("INSTALL_KEY")
if not INSTALL_KEY:
    try:
        with open(INSTALL_KEY_PATH) as f:
            INSTALL_KEY = f.read().strip()
        print("Install key loaded:", INSTALL_KEY) 
    except FileNotFoundError:
        INSTALL_KEY = None
        print("Install key NOT FOUND")

AUTH_BASE_URL = os.getenv("AUTH_BASE_URL", "https://f300aa2d1840.ngrok-free.app")
TOKEN_EXPIRY_HOURS = int(os.getenv("TOKEN_EXPIRY_HOURS", "24"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_auth_code() -> str:
    return secrets.token_urlsafe(32)

def verify_code_challenge(code_verifier: str, code_challenge: str) -> bool:
    """Verify PKCE code challenge"""
    digest = hashlib.sha256(code_verifier.encode()).digest()
    expected = base64.urlsafe_b64encode(digest).decode().rstrip('=')
    return expected == code_challenge

async def verify_mcp_token(authorization: Optional[str] = Header(None)) -> dict:
    """Validate Bearer token for MCP requests"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.split(" ")[1]
    
    for session_key, session_data in oauth_sessions.items():
        if (session_key.startswith("test_token_") and 
            session_data.get("access_token") == token and
            session_data.get("user_id") == 9999):
            
            # Check if test token is expired
            if datetime.utcnow() > session_data.get("expires_at", datetime.utcnow()):
                del oauth_sessions[session_key]
                raise HTTPException(
                    status_code=401,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            logger.info("Valid MCP request from test user")
            return {"user_id": 9999, "scopes": ["claudeai"]}
    
    db = next(get_db_connection())
    try:
        auth_token = db.query(MCPAccessToken).filter_by(token=token).first()
        
        if not auth_token or auth_token.expires_at < datetime.utcnow():
            if auth_token:
                db.delete(auth_token)
                db.commit()
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        logger.info(f"Valid MCP request from database user: {auth_token.user_id}")
        return {"user_id": auth_token.user_id, "scopes": auth_token.scope.split()}
        
    finally:
        db.close()

def create_access_token(user_id: int, expires_delta: int = 3600, scopes=None):
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    payload = {
        "sub": str(user_id),
        "scopes": scopes or ["claudeai"],
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

def ensure_claude_client(client_id: str) -> bool:
    """Ensure Claude client is registered"""
    if client_id not in registered_clients:
        if client_id.startswith("claude_client_"):
            registered_clients[client_id] = {
                "client_id": client_id,
                "redirect_uris": [
                    "https://claude.ai/api/mcp/auth_callback",
                    "https://claude.anthropic.com/api/mcp/auth_callback",
                    "https://claude.ai/api/mcp/oauth/callback",
                    "https://claude.anthropic.com/api/mcp/oauth/callback"
                ],
                "created_at": datetime.utcnow()
            }
            logger.info(f"Auto-registered Claude client: {client_id}")
            return True
        elif client_id == "test_client":
            registered_clients[client_id] = {
                "client_id": client_id,
                "redirect_uris": [
                    "http://localhost:3000/callback",
                    "https://localhost:3000/callback", 
                    "http://127.0.0.1:3000/callback",
                    "https://httpbin.org/get",  # This will show the callback data
                    f"{AUTH_BASE_URL}/test-callback"  # Our own test callback
                ],
                "created_at": datetime.utcnow()
            }
            logger.info(f"Auto-registered test client: {client_id}")
            return True
    return client_id in registered_clients