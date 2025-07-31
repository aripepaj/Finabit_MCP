import os
import logging
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict
from urllib.parse import urlencode, parse_qs

from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, Header, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from app.repositories.user_repository import UserRepository
from app.services.users import UserService
from sqlalchemy.orm import Session

from app.core.db import Base, engine, get_db_connection
from app.main_ref import mcp
from fastmcp.server.auth import BearerAuthProvider
from jose import jwt
from fastapi.staticfiles import StaticFiles

SECRET_KEY = os.environ.get("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

from app.api import sales_tool, purchases_tool, items_tool, help_tool

mcp_app = mcp.http_app(path="/mcp")
app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open("keys/private.pem", "rb") as f:
    PRIVATE_KEY = f.read()
with open("keys/public.pem", "rb") as f:
    PUBLIC_KEY = f.read()

try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {e}")
    raise

AUTH_BASE_URL = os.getenv("AUTH_BASE_URL", "https://f300aa2d1840.ngrok-free.app")
TOKEN_EXPIRY_HOURS = int(os.getenv("TOKEN_EXPIRY_HOURS", "24"))

oauth_sessions = {}

registered_clients = {}

def create_access_token(user_id: int, expires_delta: int = 3600, scopes=None):
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    payload = {
        "sub": str(user_id),
        "exp": expire,
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://claude.ai", "https://*.anthropic.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/.well-known/oauth-authorization-server")
async def oauth_metadata():
    """OAuth 2.0 Authorization Server Metadata"""
    return {
        "issuer": AUTH_BASE_URL,
        "authorization_endpoint": f"{AUTH_BASE_URL}/authorize",
        "token_endpoint": f"{AUTH_BASE_URL}/token",
        "registration_endpoint": f"{AUTH_BASE_URL}/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],  
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["claudeai"],
        "logo_uri": f"{AUTH_BASE_URL}/static/icon.ico",  
        "token_endpoint_auth_methods_supported": ["none", "client_secret_post"]
    }

@app.get("/.well-known/oauth-authorization-server/mcp")
async def oauth_metadata_mcp():
    """OAuth 2.0 Authorization Server Metadata for MCP"""
    return {
        "issuer": AUTH_BASE_URL,
        "authorization_endpoint": f"{AUTH_BASE_URL}/authorize",
        "token_endpoint": f"{AUTH_BASE_URL}/token",
        "registration_endpoint": f"{AUTH_BASE_URL}/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["claudeai"],
        "token_endpoint_auth_methods_supported": ["none", "client_secret_post"]
    }

@app.get("/.well-known/oauth-protected-resource/mcp")
async def oauth_protected_resource_mcp():
    """OAuth Protected Resource Metadata for MCP"""
    return {
        "resource": f"{AUTH_BASE_URL}/mcp",
        "authorization_servers": [AUTH_BASE_URL],
        "scopes_supported": ["claudeai"],
        "bearer_methods_supported": ["header"],
        "resource_documentation": f"{AUTH_BASE_URL}/docs"
    }

@app.post("/register")
async def register_client(request: Request):
    """OAuth 2.0 Dynamic Client Registration"""
    try:
        body = await request.json()
        client_id = f"claude_client_{secrets.token_urlsafe(16)}"
        
        # Store client info
        registered_clients[client_id] = {
            "client_id": client_id,
            "redirect_uris": body.get("redirect_uris", []),
            "created_at": datetime.utcnow()
        }
        
        logger.info(f"Registered OAuth client: {client_id}")
        
        return {
            "client_id": client_id,
            "client_id_issued_at": int(datetime.utcnow().timestamp()),
            "redirect_uris": body.get("redirect_uris", []),
            "token_endpoint_auth_method": "none",
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "scope": "claudeai"
        }
    except Exception as e:
        logger.error(f"Client registration error: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_client_metadata"}
        )

@app.get("/authorize")
async def authorize(
    response_type: str = Query(...),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query(default="claudeai"),
    state: str = Query(default=""),
    code_challenge: str = Query(...),
    code_challenge_method: str = Query(default="S256")
):
    """OAuth 2.0 Authorization Endpoint"""
    
    if not ensure_claude_client(client_id):
        logger.error(f"Unknown client_id: {client_id}")
        raise HTTPException(status_code=400, detail="Invalid client_id")
    
    client_info = registered_clients[client_id]
    if redirect_uri not in client_info["redirect_uris"]:
        logger.error(f"Invalid redirect_uri: {redirect_uri} for client {client_id}")
        logger.info(f"Valid redirect_uris: {client_info['redirect_uris']}")
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")
    
    auth_request_id = secrets.token_urlsafe(16)
    oauth_sessions[auth_request_id] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "created_at": datetime.utcnow()
    }
    
    logger.info(f"Authorization request from Claude client: {client_id}")
    logger.info(f"Redirect URI: {redirect_uri}")
    logger.info(f"Scope: {scope}")
    
    login_form = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Finabit MCP Authorization</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            max-width: 500px; margin: 100px auto; padding: 20px; background: #f8fafc;
        }}
        .container {{
            background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .finabit-logo {{ margin: 0 auto 10px; width: 72px; height: 72px; }}
        h2 {{ color: #1f2937; margin: 10px 0; }}
        label {{ display: block; margin: 15px 0 5px; font-weight: 500; }}
        input {{ width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; 
                font-size: 16px; box-sizing: border-box; }}
        input:focus {{ outline: none; border-color: #2563eb; }}
        button {{ background: #2563eb; color: white; padding: 12px 24px; border: none; 
                border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 20px; }}
        button:hover {{ background: #1d4ed8; }}
        .error {{ background: #fee2e2; color: #dc2626; padding: 10px; border-radius: 6px; margin: 10px 0; }}
        .testing-hint {{ margin-top: 15px; padding: 10px; background: #f0f9ff; border-radius: 6px; font-size: 14px; color: #0369a1; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="/static/icon.ico" class="finabit-logo" alt="Finabit Logo">
            <h2>Sign in to Finabit</h2>
        </div>
        <form method="post" action="/authorize">
            <input type="hidden" name="auth_request_id" value="{auth_request_id}">
            <label>Username:</label>
            <input name="username" required autocomplete="username" placeholder="test">
            <label>Password:</label>
            <input type="password" name="password" required autocomplete="current-password" placeholder="test">
            <button type="submit">Authorize</button>
            <div class="testing-hint">
                <strong>💡 For testing:</strong> Use username "test" and password "test"
            </div>
        </form>
    </div>
</body>
</html>
"""
    
    return HTMLResponse(login_form)

@app.post("/authorize")
async def process_authorization(
    request: Request,
    auth_request_id: str = Form(...),
    username: str = Form(...),
    password: str = Form(...)
):
    if auth_request_id not in oauth_sessions:
        raise HTTPException(status_code=400, detail="Invalid authorization request")
    session = oauth_sessions[auth_request_id]

    if username == "test" and password == "test":
        user_id = 9999
        auth_code = generate_auth_code()
        oauth_sessions[f"code_{auth_code}"] = {
            "user_id": user_id,
            "client_id": session["client_id"],
            "scope": session["scope"],
            "code_challenge": session["code_challenge"],
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        }
        del oauth_sessions[auth_request_id]

        redirect_url = (
            f"{session['redirect_uri']}?"
            f"{urlencode({'code': auth_code, 'state': session['state']})}"
        )
        logger.info(f"Redirecting (test user) via GET: {redirect_url}")
        return RedirectResponse(url=redirect_url, status_code=302)

    db = next(get_db_connection())
    try:
        service = UserService(db)
        user = service.authenticate_user(username, password) 
        if not user:
            # show login form again with error
            return HTMLResponse(login_form_html(auth_request_id, error_message="Invalid username or password."), status_code=200)

        auth_code = generate_auth_code()
        oauth_sessions[f"code_{auth_code}"] = {
            "user_id": user["UserID"],
            "client_id": session["client_id"],
            "scope": session["scope"],
            "code_challenge": session["code_challenge"],
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        }
        del oauth_sessions[auth_request_id]

        redirect_url = (
            f"{session['redirect_uri']}?"
            f"{urlencode({'code': auth_code, 'state': session['state']})}"
        )
        logger.info(f"Redirecting (real user) via GET: {redirect_url}")
        return RedirectResponse(url=redirect_url, status_code=302)
    finally:
        db.close()

def login_form_html(auth_request_id, error_message=None):
    error_block = ""
    if error_message:
        error_block = f'<div class="error">{error_message}</div>'
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Finabit MCP Authorization</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            max-width: 500px; margin: 100px auto; padding: 20px; background: #f8fafc;
        }}
        .container {{
            background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .finabit-logo {{ margin: 0 auto 10px; width: 72px; height: 72px; }}
        h2 {{ color: #1f2937; margin: 10px 0; }}
        label {{ display: block; margin: 15px 0 5px; font-weight: 500; }}
        input {{ width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; 
                font-size: 16px; box-sizing: border-box; }}
        input:focus {{ outline: none; border-color: #2563eb; }}
        button {{ background: #2563eb; color: white; padding: 12px 24px; border: none; 
                border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 20px; }}
        button:hover {{ background: #1d4ed8; }}
        .error {{ background: #fee2e2; color: #dc2626; padding: 10px; border-radius: 6px; margin: 10px 0; }}
        .testing-hint {{ margin-top: 15px; padding: 10px; background: #f0f9ff; border-radius: 6px; font-size: 14px; color: #0369a1; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="/static/icon.ico" class="finabit-logo" alt="Finabit Logo">
            <h2>Sign in to Finabit</h2>
        </div>
        <form method="post" action="/authorize">
            <input type="hidden" name="auth_request_id" value="{auth_request_id}">
            {error_block}
            <label>Username:</label>
            <input name="username" required autocomplete="username" placeholder="test">
            <label>Password:</label>
            <input type="password" name="password" required autocomplete="current-password" placeholder="test">
            <button type="submit">Authorize</button>
            <div class="testing-hint">
                <strong>💡 For testing:</strong> Use username "test" and password "test"
            </div>
        </form>
    </div>
</body>
</html>
"""

@app.post("/token")
async def token_endpoint(request: Request):
    """OAuth 2.0 Token Endpoint"""
    try:
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            data = await request.json()
        else:
            form_data = await request.form()
            data = dict(form_data)
        
        logger.info(f"Token request data: {data}")
        
        grant_type = data.get("grant_type")
        auth_code = data.get("code")
        redirect_uri = data.get("redirect_uri")
        client_id = data.get("client_id")
        code_verifier = data.get("code_verifier")
        
        logger.info(f"Token request: grant_type={grant_type}, code={auth_code[:10] if auth_code else None}..., client_id={client_id}")
        
        if grant_type != "authorization_code":
            logger.error(f"Unsupported grant type: {grant_type}")
            return JSONResponse(
                status_code=400,
                content={"error": "unsupported_grant_type", "error_description": f"Grant type '{grant_type}' not supported"}
            )
        
        if not auth_code:
            logger.error("Missing authorization code")
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "error_description": "Missing authorization code"}
            )
        
        code_key = f"code_{auth_code}"
        if code_key not in oauth_sessions:
            logger.error(f"Invalid authorization code: {auth_code}")
            logger.info(f"Available codes: {[k for k in oauth_sessions.keys() if k.startswith('code_')]}")
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_grant", "error_description": "Authorization code not found or expired"}
            )
        
        code_data = oauth_sessions[code_key]
        logger.info(f"Found code data: user_id={code_data.get('user_id')}, client_id={code_data.get('client_id')}")
        
        if datetime.utcnow() > code_data["expires_at"]:
            logger.error("Authorization code expired")
            del oauth_sessions[code_key]
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_grant", "error_description": "Authorization code expired"}
            )
        
        if code_verifier and not verify_code_challenge(code_verifier, code_data["code_challenge"]):
            logger.error("PKCE verification failed")
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_grant", "error_description": "PKCE verification failed"}
            )
        
        user_id = code_data["user_id"]
        scope = code_data["scope"].split() if isinstance(code_data["scope"], str) else ["claudeai"]
        access_token = create_access_token(user_id, expires_delta=TOKEN_EXPIRY_HOURS * 3600, scopes=scope)

        expires_at = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        
        logger.info(f"Generating access token for user_id: {code_data['user_id']}")
        
        if code_data["user_id"] == 9999:
            logger.info("Issuing access token for test user (not stored in DB)")
            
            test_token_key = f"test_token_{access_token}"
            oauth_sessions[test_token_key] = {
                "user_id": 9999,
                "scope": code_data["scope"],
                "expires_at": expires_at,
                "access_token": access_token
            }
            
            del oauth_sessions[code_key]
            
            response_data = {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": TOKEN_EXPIRY_HOURS * 3600,
                "scope": code_data["scope"]
            }
            
            logger.info(f"Returning token response: {response_data}")
            return response_data
        
        del oauth_sessions[code_key]
        response_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": TOKEN_EXPIRY_HOURS * 3600,
            "scope": code_data["scope"]
            }
        
        logger.info(f"Returning token response: {response_data}")
        return response_data
            
    except Exception as e:
        logger.error(f"Token endpoint error: {e}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_request", "error_description": str(e)}
        )

app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting OAuth MCP Server for Claude...")
    uvicorn.run(app, host="0.0.0.0", port=10000)